"""EOD D2 checkpoint — triage end-to-end smoke.

Two checks, PASS/FAIL with an exit code:

  A. Coverage — every triaged issue carries a valid priority enum + non-empty
     repro_steps, and triaged data exists for all three sources (github / slack /
     email). This is what the App's detail view renders, so it proves "real
     triaged data (incl. seeded) shows priority+repro".
  B. Live loop — create a throwaway issue, run the real triage agent over it, and
     assert the agent → normalize_priority round-trip wrote back a valid priority,
     repro steps, and status='triaged'. Then clean up.

Run:  .venv/Scripts/python.exe scripts/smoke_triage.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pod.lemma_client import get_pod, load_env  # noqa: E402
from pod.tables.issues_table import PRIORITIES, TABLE_NAME  # noqa: E402
from ingest.triage.run_triage import triage_one  # noqa: E402

VALID = set(PRIORITIES)
SMOKE_ID = "smoke_triage_e2e"
SMOKE_ISSUE = {
    "id": SMOKE_ID,
    "source": "github",
    "external_id": "0",
    "title": "App crashes on every startup after the 3.0 upgrade",
    "body": (
        "After upgrading to 3.0 the app crashes immediately on launch with a "
        "null-pointer in auth/session.go. It fails 100% of the time and there is "
        "no workaround other than downgrading. Steps: 1) install 3.0  2) run the "
        "binary  3) it crashes before the login screen."
    ),
    "status": "new",
    "related_ids": [],
    "linked_prs": [],
}


def _repro_ok(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def check_coverage(pod) -> tuple[bool, str]:
    items = pod.records.list(TABLE_NAME, limit=300).to_dict()["items"]
    triaged = [i for i in items if i.get("status") == "triaged"]
    if not triaged:
        return False, "no triaged issues found"

    bad = [
        i["id"] for i in triaged
        if i.get("priority") not in VALID or not _repro_ok(i.get("repro_steps"))
    ]
    if bad:
        return False, f"{len(bad)} triaged issue(s) missing valid priority/repro: {bad[:5]}"

    sources = {i["source"] for i in triaged}
    missing = {"github", "slack", "email"} - sources
    if missing:
        return False, f"no triaged data for source(s): {sorted(missing)}"

    return True, f"{len(triaged)} triaged issues, all with priority+repro, across {sorted(sources)}"


def check_live_loop(pod) -> tuple[bool, str]:
    # Fresh row each run.
    try:
        pod.records.delete(TABLE_NAME, SMOKE_ID)
    except Exception:
        pass
    pod.records.create(TABLE_NAME, SMOKE_ISSUE)
    try:
        triage_one(pod, SMOKE_ID)
        got = pod.records.get(TABLE_NAME, SMOKE_ID)
        if got.get("status") != "triaged":
            return False, f"status not triaged: {got.get('status')!r}"
        if got.get("priority") not in VALID:
            return False, f"invalid priority: {got.get('priority')!r}"
        if not _repro_ok(got.get("repro_steps")):
            return False, "repro_steps empty"
        return True, (
            f"agent triaged the smoke issue -> priority={got['priority']}, "
            f"repro={got['repro_steps'].splitlines()[0][:50]!r}…"
        )
    finally:
        try:
            pod.records.delete(TABLE_NAME, SMOKE_ID)
        except Exception:
            pass


def main() -> int:
    load_env()
    pod = get_pod()
    failed = False

    for name, fn in (("coverage", check_coverage), ("live loop", check_live_loop)):
        try:
            ok, detail = fn(pod)
        except Exception as exc:
            ok, detail = False, f"raised {type(exc).__name__}: {exc}"
        print(f"{'PASS' if ok else 'FAIL'} [{name}] {detail}")
        failed = failed or not ok

    print("SMOKE PASS" if not failed else "SMOKE FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
