"""Box 5 — github_fetch: pull open issues from a public repo (read-only PAT).

GitHub is the one source that is NOT a Lemma Surface, so this is the connector
we build ourselves. Read-only via a Personal Access Token (public repos work
without one too, just at a lower rate limit).

Used as a library (``fetch_open_issues``) by the ingest step, and runnable
directly for a quick manual check:

    GITHUB_REPO=python/cpython .venv/Scripts/python.exe ingest/github/github_fetch.py
"""

from __future__ import annotations

import os
import pathlib
import sys

import requests

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from pod.lemma_client import load_env  # noqa: E402

API_ROOT = "https://api.github.com"


def fetch_open_issues(repo: str, token: str | None = None, limit: int = 30) -> list[dict]:
    """Return up to ``limit`` open issues for ``repo`` (``owner/name``).

    Pull requests are excluded (the GitHub issues endpoint includes PRs; we drop
    any entry carrying a ``pull_request`` key). Each item is normalized to the
    fields the ingest step needs.
    """
    if "/" not in repo:
        raise ValueError(f"repo must be 'owner/name', got {repo!r}")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    resp = requests.get(
        f"{API_ROOT}/repos/{repo}/issues",
        headers=headers,
        params={"state": "open", "per_page": min(limit, 100)},
        timeout=20,
    )
    if resp.status_code != 200:
        raise RuntimeError(
            f"GitHub API {resp.status_code} for {repo}: {resp.text[:200]}"
        )

    issues: list[dict] = []
    for raw in resp.json():
        if "pull_request" in raw:  # skip PRs returned by the issues endpoint
            continue
        issues.append(
            {
                "external_id": str(raw["number"]),
                "title": raw.get("title") or "(no title)",
                "body": raw.get("body") or "",
                "url": raw.get("html_url", ""),
                "created_at": raw.get("created_at", ""),
                "labels": [lbl["name"] for lbl in raw.get("labels", [])],
            }
        )
        if len(issues) >= limit:
            break
    return issues


def main() -> int:
    load_env()
    repo = os.environ.get("GITHUB_REPO")
    if not repo:
        print("FAIL: set GITHUB_REPO (owner/name) in .env or the environment.")
        return 1
    issues = fetch_open_issues(repo, os.environ.get("GITHUB_PAT"))
    print(f"PASS: fetched {len(issues)} open issues from {repo}.")
    for it in issues[:5]:
        print(f"  #{it['external_id']}  {it['title'][:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
