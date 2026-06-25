"""Box 1 — verify the pod connection.

Constructing a Pod object is not proof of anything; this makes a real
authenticated call (list tables) so a green run means creds + network work.

Run:  .venv/Scripts/python.exe scripts/check_connection.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from lemma_sdk import LemmaError  # noqa: E402

from pod.lemma_client import get_pod  # noqa: E402


def main() -> int:
    try:
        pod = get_pod()
    except Exception as exc:  # config/auth resolution before any network call
        print(f"FAIL: could not build pod connection: {exc}")
        print("  -> Set LEMMA_POD_ID + LEMMA_TOKEN in .env, or run `lemma auth login`.")
        return 1

    try:
        tables = pod.tables.list().items
    except LemmaError as exc:
        print(f"FAIL: connected object built but API call failed: {exc}")
        return 1

    pod_id = getattr(pod, "pod_id", "?")
    base_url = getattr(pod, "base_url", "?")
    print(f"PASS: connected to pod {pod_id} at {base_url}")
    print(f"  tables present: {sorted(t.name for t in tables) or '(none yet)'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
