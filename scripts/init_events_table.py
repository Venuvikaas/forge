"""Create the ``events`` audit-trail Table in the pod (idempotent).

Run:  .venv/Scripts/python.exe scripts/init_events_table.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pod.lemma_client import get_pod  # noqa: E402
from pod.tables.events_table import TABLE_NAME, ensure_events_table  # noqa: E402


def main() -> int:
    pod = get_pod()
    created = ensure_events_table(pod)
    if created:
        print(f"PASS: created table '{TABLE_NAME}'.")
    else:
        print(f"PASS: table '{TABLE_NAME}' already exists (no-op).")

    detail = pod.tables.get(TABLE_NAME)
    cols = [c.name for c in detail.columns]
    print(f"  columns: {cols}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
