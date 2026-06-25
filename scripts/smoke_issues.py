"""Box 3 — issues Table round-trip: create a record, read it back, clean up.

Run:  .venv/Scripts/python.exe scripts/smoke_issues.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pod.lemma_client import get_pod  # noqa: E402
from pod.tables.issues_table import TABLE_NAME, ensure_issues_table  # noqa: E402

SAMPLE = {
    "id": "smoke_roundtrip",
    "source": "github",
    "external_id": "0",
    "title": "Round-trip smoke test",
    "body": "If you can read this back, Tables work.",
    "status": "new",
    "related_ids": [],
    "linked_prs": [],
}


def main() -> int:
    pod = get_pod()
    ensure_issues_table(pod)

    rid = SAMPLE["id"]
    try:
        pod.records.create(TABLE_NAME, SAMPLE)
        got = pod.records.get(TABLE_NAME, rid)
        assert got["title"] == SAMPLE["title"], f"title mismatch: {got.get('title')!r}"
        assert got["source"] == "github", f"source mismatch: {got.get('source')!r}"
        print(f"PASS: created and read back record '{rid}' -> {got['title']!r}")
        return 0
    except Exception as exc:
        print(f"FAIL: round-trip failed: {exc}")
        return 1
    finally:
        try:
            pod.records.delete(TABLE_NAME, rid)
            print(f"  cleaned up record '{rid}'")
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
