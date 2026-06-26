#input_type_name: LinkRelatedInput
#output_type_name: LinkRelatedResult
#function_name: link_related

"""Record a confirmed duplicate link on both issues (docs/contracts.md §1).

related_ids is symmetric: if A is a duplicate of B, opening either should show the
other. This appends each id to the other's list, idempotently (re-running never
creates dupes), and is the single granted writer of related_ids.
"""

from typing import List

from pydantic import BaseModel
from lemma_sdk import Pod


class LinkRelatedInput(BaseModel):
    id_a: str
    id_b: str


class LinkRelatedResult(BaseModel):
    id_a: str
    id_b: str
    a_related_ids: List[str]
    b_related_ids: List[str]
    changed: bool


def _with(existing, other: str) -> tuple[list, bool]:
    ids = list(existing or [])
    if other in ids:
        return ids, False
    ids.append(other)
    return ids, True


async def link_related(ctx, data: LinkRelatedInput) -> LinkRelatedResult:
    if data.id_a == data.id_b:
        raise ValueError("cannot link an issue to itself")

    pod = Pod.from_env()
    t = pod.table("issues")

    row_a = t.get(data.id_a)
    row_b = t.get(data.id_b)

    a_ids, a_changed = _with(row_a.get("related_ids"), data.id_b)
    b_ids, b_changed = _with(row_b.get("related_ids"), data.id_a)

    if a_changed:
        t.update(data.id_a, {"related_ids": a_ids})
    if b_changed:
        t.update(data.id_b, {"related_ids": b_ids})

    return LinkRelatedResult(
        id_a=data.id_a,
        id_b=data.id_b,
        a_related_ids=a_ids,
        b_related_ids=b_ids,
        changed=a_changed or b_changed,
    )
