"""Migration — add the override / multi-source columns to the live ``issues`` table.

Two additive, nullable TEXT columns (``add_column`` is additive — no delete+recreate,
existing rows untouched):

  - ``assignee``       — operator-assigned owner (null = Unassigned). The human
                          override controls in the App write this.
  - ``source_account`` — the specific origin within a source: the GitHub repo
                          (``cli/cli``), Slack channel (``#eng-help``) or mailbox
                          (``support@``). This is the dimension the App's
                          repo/workspace/mailbox switcher groups by (multi-repo).

Idempotent: each column is a no-op if already present.

    .venv/Scripts/python.exe scripts/add_override_columns.py
"""

from __future__ import annotations

import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from lemma_sdk.openapi_client.models.add_column_request import AddColumnRequest  # noqa: E402

from pod.lemma_client import get_pod, load_env  # noqa: E402
from pod.tables.issues_table import TABLE_NAME  # noqa: E402

# column name -> description
COLUMNS = {
    "assignee": "operator-assigned owner; null = Unassigned (App human-override control)",
    "source_account": "origin within the source: repo (cli/cli), Slack channel (#eng-help), or mailbox (support@) — the switcher's grouping key",
}


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

    failed = False
    for column, description in COLUMNS.items():
        if column in _existing_columns(pod):
            print(f"PASS: column {column!r} already present on {TABLE_NAME!r} (no-op)")
            continue
        request = AddColumnRequest.from_dict(
            {"column": {"name": column, "type": "TEXT", "description": description}}
        )
        pod.tables.add_column(TABLE_NAME, request)
        if column in _existing_columns(pod):
            print(f"PASS: added column {column!r} to {TABLE_NAME!r}")
        else:
            print(f"FAIL: add_column returned but {column!r} not present on {TABLE_NAME!r}")
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
