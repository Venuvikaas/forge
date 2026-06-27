"""Backfill ``triage_reason`` for rows triaged before the column existed.

The triage agent always produced a one-sentence ``reason`` (contract §3), but it
was only persisted once ``normalize_priority`` learned to write the new
``triage_reason`` column. Already-triaged rows therefore have a null reason.

This re-runs the **read-only** triage agent per such row to recover its rationale
and writes back **only** ``triage_reason`` — priority, repro_steps and status are
left exactly as curated, so the demo dataset is undisturbed.

Tolerates the flaky backend: a per-row failure is logged and skipped (the row
keeps a null reason; the App simply hides the block), and the run can be re-run to
fill the gaps.

    .venv/Scripts/python.exe scripts/backfill_triage_reason.py            # all triaged rows missing a reason
    .venv/Scripts/python.exe scripts/backfill_triage_reason.py gh_142     # one row
"""

from __future__ import annotations

import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from pod.lemma_client import get_pod, load_env  # noqa: E402
from pod.tables.issues_table import TABLE_NAME  # noqa: E402
from ingest.triage.run_triage import run_agent, LOG_DIR  # noqa: E402


def _reason_from_log(issue_id: str) -> str | None:
    """Recover a previously-logged triage reason without hitting the agent.

    The flaky backend makes a live agent re-run unreliable; when a row was
    triaged on this machine its rationale is already in logs/triage/<id>.json,
    so replay it offline.
    """
    log = LOG_DIR / f"{issue_id}.json"
    if not log.exists():
        return None
    try:
        verdict = json.loads(log.read_text(encoding="utf-8")).get("verdict", {})
    except Exception:
        return None
    return (verdict.get("reason") or "").strip() or None


def _needs_reason(row: dict) -> bool:
    return row.get("status") == "triaged" and not (row.get("triage_reason") or "").strip()


def _rows_missing_reason(pod, limit: int = 200) -> list[dict]:
    items = pod.records.list(
        TABLE_NAME,
        limit=limit,
        filter=[{"field": "status", "op": "eq", "value": "triaged"}],
    ).to_dict().get("items", [])
    return [r for r in items if _needs_reason(r)]


def backfill_one(pod, issue_id: str, use_agent: bool = True) -> str | None:
    """Recover and write ``triage_reason`` for one row. Returns the reason or None.

    Prefers an offline log replay (instant, survives a degraded backend); falls
    back to a live read-only agent run when no log exists and ``use_agent``.
    """
    reason = _reason_from_log(issue_id)
    if not reason and use_agent:
        issue = pod.records.get(TABLE_NAME, issue_id)
        verdict = run_agent(pod, issue)
        reason = (verdict.get("reason") or "").strip()
    if not reason:
        return None
    pod.table(TABLE_NAME).update(issue_id, {"triage_reason": reason})
    return reason


def main() -> int:
    load_env()
    pod = get_pod()

    args = [a for a in sys.argv[1:] if a != "--logs-only"]
    # --logs-only: replay reasons from logs only, never call the (flaky) agent.
    use_agent = "--logs-only" not in sys.argv

    if args:
        targets = [args[0]]
    else:
        targets = [r["id"] for r in _rows_missing_reason(pod)]

    print(f"backfill triage_reason: {len(targets)} row(s)" + ("" if use_agent else " (logs-only)"))
    ok = failed = 0
    for issue_id in targets:
        try:
            reason = backfill_one(pod, issue_id, use_agent=use_agent)
            if reason:
                print(f"  [ok] {issue_id}: {reason[:80]}")
                ok += 1
            else:
                print(f"  [skip] {issue_id}: agent produced no reason")
                failed += 1
        except Exception as exc:  # tolerate the flaky backend; re-run fills gaps
            print(f"  [skip] {issue_id}: {exc}")
            failed += 1

    print(f"PASS: backfilled {ok}/{len(targets)} ({failed} skipped)")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
