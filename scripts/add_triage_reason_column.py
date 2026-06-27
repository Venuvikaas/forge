"""Migration — add the ``triage_reason`` column to the live ``issues`` table.

The triage agent already produces a one-sentence ``reason`` (contract §3) but it
was never stored, so the App could not surface *why* the AI picked a priority.
This adds a nullable TEXT column for it. ``add_column`` is additive (no
delete+recreate), so existing rows and data are untouched.

Idempotent: a no-op if the column already exists.

    .venv/Scripts/python.exe scripts/add_triage_reason_column.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from lemma_sdk.openapi_client.models.add_column_request import AddColumnRequest  # noqa: E402

from pod.lemma_client import get_pod, load_env  # noqa: E402
from pod.tables.issues_table import TABLE_NAME  # noqa: E402

COLUMN = "triage_reason"


def _existing_columns(pod) -> set[str]:
    detail = pod.tables.get(TABLE_NAME)
    cols = getattr(detail, "columns", None) or []
    names = set()
    for c in cols:
        name = getattr(c, "name", None) or (c.get("name") if isinstance(c, dict) else None)
        if name:
            names.add(name)
    return names


def main() -> int:
    load_env()
    pod = get_pod()

    if COLUMN in _existing_columns(pod):
        print(f"PASS: column {COLUMN!r} already present on {TABLE_NAME!r} (no-op)")
        return 0

    request = AddColumnRequest.from_dict(
        {
            "column": {
                "name": COLUMN,
                "type": "TEXT",
                "description": "one-sentence AI triage rationale (contract §3 'reason'); null until triaged",
            }
        }
    )
    pod.tables.add_column(TABLE_NAME, request)

    if COLUMN in _existing_columns(pod):
        print(f"PASS: added column {COLUMN!r} to {TABLE_NAME!r}")
        return 0
    print(f"FAIL: add_column returned but {COLUMN!r} not present on {TABLE_NAME!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
