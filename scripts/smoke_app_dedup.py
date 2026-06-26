"""EOD D3 checkpoint — verify dedup is visible in the app.

The app (app/index.html) renders the "N related" badge from
`issue.related_ids.length` and the detail-view related panel by resolving each
related id against the loaded issues (findIssue -> clickable selectIssue). This
script asserts the LIVE data behind that view holds, so opening a critical bug
in the app shows real related issues:

  - the demo-anchor pairs are linked (gh_142<->iss_003, gh_158<->iss_007);
  - at least one CRITICAL bug has >=1 related id (the checkpoint requirement);
  - every related id on a critical bug resolves to an existing row, is a
    DIFFERENT source (a real cross-source duplicate), and the link is symmetric
    (so the panel works from either side).

Run:  .venv/Scripts/python.exe scripts/smoke_app_dedup.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from pod.lemma_client import get_pod, load_env  # noqa: E402
from pod.tables.issues_table import TABLE_NAME  # noqa: E402

# The pairs the demo script opens on camera (docs/demo-script.md "Demo Anchors").
ANCHORS = [("gh_142", "iss_003"), ("gh_158", "iss_007")]


def main() -> int:
    load_env()
    pod = get_pod()
    items = {i["id"]: i for i in pod.records.list(TABLE_NAME, limit=300).to_dict()["items"]}
    failed = False

    def rel(i):  # what app's relatedCount() reads
        return items[i].get("related_ids") or []

    # 1) Demo-anchor pairs are linked symmetrically.
    for gh_id, iss_id in ANCHORS:
        ok = gh_id in items and iss_id in items and iss_id in rel(gh_id) and gh_id in rel(iss_id)
        print(f"{'PASS' if ok else 'FAIL'} anchor {gh_id} <-> {iss_id} linked both ways")
        failed = failed or not ok

    # 2) At least one CRITICAL bug shows real related issues, and every related
    #    link on a critical bug is resolvable + cross-source + symmetric.
    criticals = [i for i in items.values() if i.get("priority") == "critical"]
    linked_criticals = [i for i in criticals if rel(i["id"])]
    if not linked_criticals:
        print("FAIL no critical bug has any related issue")
        failed = True
    for c in linked_criticals:
        for rid in rel(c["id"]):
            target = items.get(rid)
            resolvable = target is not None
            cross_source = resolvable and target["source"] != c["source"]
            symmetric = resolvable and c["id"] in (target.get("related_ids") or [])
            ok = resolvable and cross_source and symmetric
            print(
                f"{'PASS' if ok else 'FAIL'} critical {c['id']} -> {len(rel(c['id']))} related; "
                f"{rid} resolvable={resolvable} cross_source={cross_source} symmetric={symmetric}"
            )
            failed = failed or not ok
        print(f"     (app would show '{len(rel(c['id']))} related' on {c['id']} "
              f"[{c['title'][:40]}…])")

    print("APP-DEDUP SMOKE PASS" if not failed else "APP-DEDUP SMOKE FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
