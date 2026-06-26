#input_type_name: FetchSourceEvidenceInput
#output_type_name: FetchSourceEvidenceResult
#function_name: fetch_source_evidence
#config_type_name: FetchSourceEvidenceConfig

"""Ground the crashing symbol in REAL source — the D5 hero (verifiable investigation).

Reads the issue, parses the Go stack frame (`<module>/<pkg>.<symbol>(...)`) for the
package path + symbol, then locates that symbol in the actual repository using only
PUBLIC GitHub endpoints:

  1. the latest commit sha           (api.github.com — pins a stable blob URL)
  2. the recursive file tree         (api.github.com — paths + blob shas, no auth)
  3. the raw file contents           (raw.githubusercontent.com — a CDN, not rate-limited)

then greps the file for the symbol's definition and returns the matched lines plus a
real ``blob/<sha>/<path>#Lstart-Lend`` URL anchored to where the code actually lives.

Hard rule: **never fabricate.** If the symbol cannot be found in real source, return
``found=false`` with empty evidence — the synthesis agent then proposes no diff. A
cited line is only emitted when it was read from the actual repository.
"""

import re
from typing import List, Optional

import requests
from pydantic import BaseModel
from lemma_sdk import Pod

API_ROOT = "https://api.github.com"
RAW_ROOT = "https://raw.githubusercontent.com"
_UA = {"User-Agent": "forge-investigate"}   # GitHub rejects requests with no UA
_SRC_EXT = (".go", ".py", ".js", ".ts", ".rb", ".rs", ".java")

# A Go panic frame: `github.com/cli/cli/v2/pkg/cmd/pr/create.getRemotes(...)`
_FRAME = re.compile(r"((?:[\w.-]+/)+[\w.-]+)\.([A-Za-z_]\w*)\s*\(")
# A bare dotted reference: `create.getRemotes`
_DOTTED = re.compile(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\b")


class FetchSourceEvidenceInput(BaseModel):
    issue_id: str
    symbol: Optional[str] = None          # override; otherwise parsed from the issue
    keywords: List[str] = []              # fallback narrowing when no package path


class FetchSourceEvidenceConfig(BaseModel):
    default_repo: str = "cli/cli"
    max_candidates: int = 12              # cap raw fetches; CDN, but stay bounded


class CodeEvidence(BaseModel):
    type: str = "code"
    label: str
    url: str                              # blob/<sha>/<path>#Lstart-Lend
    file_path: str
    symbol: str
    line_start: int
    line_end: int
    snippet: str                          # the real matched lines, verbatim


class FetchSourceEvidenceResult(BaseModel):
    issue_id: str
    found: bool
    symbol: str = ""
    package_path: str = ""                # repo-relative, e.g. pkg/cmd/pr/create
    repo: str = ""
    sha: str = ""
    evidence: Optional[CodeEvidence] = None


def _repo_relative(pkg: str) -> str:
    """`github.com/cli/cli/v2/pkg/cmd/pr/create` -> `pkg/cmd/pr/create`."""
    parts = [p for p in pkg.split("/") if p]
    if len(parts) >= 3 and "." in parts[0]:      # host/owner/repo prefix
        parts = parts[3:]
    if parts and re.fullmatch(r"v\d+", parts[0]):  # go module major version
        parts = parts[1:]
    return "/".join(parts)


def _parse_frame(text: str):
    """Return (symbol, repo_relative_package) parsed from a stack frame, best first."""
    for pkg, sym in _FRAME.findall(text):
        rel = _repo_relative(pkg)
        if rel:
            return sym, rel
    # No fully-qualified frame: take the last `pkg.symbol` dotted reference.
    dotted = _DOTTED.findall(text)
    if dotted:
        return dotted[-1][1], ""
    return "", ""


def _http_json(url: str, params: dict):
    r = requests.get(url, headers={**_UA, "Accept": "application/vnd.github+json"},
                     params=params, timeout=15)
    return r.json() if r.status_code == 200 else None


def _select_candidates(paths: List[str], package_path: str, symbol: str,
                       keywords: List[str], limit: int) -> List[str]:
    src = [p for p in paths if p.endswith(_SRC_EXT) and not p.endswith("_test.go")]
    # 1) Exact package directory from the stack frame — the strongest signal.
    if package_path:
        scoped = [p for p in src if p.startswith(package_path + "/")
                  and "/" not in p[len(package_path) + 1:]]
        if scoped:
            return scoped[:limit]
    # 2) Fall back to path tokens (symbol + keyword words).
    toks = set()
    for kw in [symbol, *keywords]:
        for t in re.split(r"[^a-zA-Z0-9]+", (kw or "").lower()):
            if len(t) >= 4:
                toks.add(t)
    scored = sorted(
        ((sum(t in p.lower() for t in toks), p) for p in src),
        key=lambda x: -x[0],
    )
    return [p for s, p in scored if s > 0][:limit]


def _grep_symbol(content: str, symbol: str):
    """Find the symbol's definition (preferred) or first reference. Returns
    (line_start, line_end, snippet) 1-indexed, or None."""
    lines = content.splitlines()
    def_re = re.compile(rf"^\s*(?:func|def|class|type|const|var)\b.*\b{re.escape(symbol)}\b")
    bare_re = re.compile(rf"\b{re.escape(symbol)}\b")

    start_idx = next((i for i, l in enumerate(lines) if def_re.search(l)), None)
    if start_idx is not None:
        end_idx = start_idx
        for j in range(start_idx + 1, min(start_idx + 40, len(lines))):
            end_idx = j
            if re.match(r"^[}\)]", lines[j]):       # column-0 close = end of block
                break
        else:
            end_idx = min(start_idx + 12, len(lines) - 1)
    else:
        hit = next((i for i, l in enumerate(lines) if bare_re.search(l)), None)
        if hit is None:
            return None
        start_idx = max(0, hit - 2)
        end_idx = min(len(lines) - 1, hit + 4)

    snippet = "\n".join(lines[start_idx:end_idx + 1])
    return start_idx + 1, end_idx + 1, snippet


async def fetch_source_evidence(ctx, data: FetchSourceEvidenceInput) -> FetchSourceEvidenceResult:
    cfg = ctx.config or FetchSourceEvidenceConfig()
    repo = getattr(cfg, "default_repo", "cli/cli")
    limit = getattr(cfg, "max_candidates", 12)

    pod = Pod.from_env()
    try:
        issue = pod.table("issues").get(data.issue_id)
    except Exception:
        issue = {}
    body = f"{issue.get('title', '')}\n{issue.get('body', '')}"

    parsed_symbol, package_path = _parse_frame(body)
    symbol = (data.symbol or parsed_symbol or "").strip()

    empty = FetchSourceEvidenceResult(
        issue_id=data.issue_id, found=False, symbol=symbol,
        package_path=package_path, repo=repo,
    )
    if not symbol:
        return empty

    commits = _http_json(f"{API_ROOT}/repos/{repo}/commits", {"per_page": 1})
    if not commits:
        return empty
    sha = commits[0].get("sha", "")
    empty.sha = sha

    tree = _http_json(f"{API_ROOT}/repos/{repo}/git/trees/{sha}", {"recursive": 1})
    if not tree:
        return empty
    paths = [t["path"] for t in tree.get("tree", []) if t.get("type") == "blob"]

    candidates = _select_candidates(paths, package_path, symbol,
                                    data.keywords, limit)
    for path in candidates:
        r = requests.get(f"{RAW_ROOT}/{repo}/{sha}/{path}", headers=_UA, timeout=15)
        if r.status_code != 200:
            continue
        hit = _grep_symbol(r.text, symbol)
        if not hit:
            continue
        line_start, line_end, snippet = hit
        url = f"https://github.com/{repo}/blob/{sha}/{path}#L{line_start}-L{line_end}"
        return FetchSourceEvidenceResult(
            issue_id=data.issue_id, found=True, symbol=symbol,
            package_path=package_path, repo=repo, sha=sha,
            evidence=CodeEvidence(
                label=f"{path}:{line_start} — {symbol}()",
                url=url, file_path=path, symbol=symbol,
                line_start=line_start, line_end=line_end, snippet=snippet,
            ),
        )

    return empty   # symbol not found in real source — never fabricate
