#input_type_name: NormalizePriorityInput
#output_type_name: NormalizePriorityResult
#function_name: normalize_priority

"""Validate-and-write the triage verdict (docs/contracts.md §3).

The triage agent is read-only and emits ``{priority, repro_steps, reason}``. An
LLM can drift outside the enum or omit a field, so the priority never reaches the
table unvalidated: this function coerces it to the contract enum (unknown/missing
-> ``normal``) and is the single granted writer that stamps the row ``triaged``.
"""

from typing import Optional

from pydantic import BaseModel
from lemma_sdk import Pod

# The issues.priority enum, kept in sync with docs/contracts.md §1.
VALID_PRIORITIES = {"critical", "high", "normal", "low"}
DEFAULT_PRIORITY = "normal"


class NormalizePriorityInput(BaseModel):
    issue_id: str
    priority: Optional[str] = None
    repro_steps: Optional[str] = None
    reason: Optional[str] = None


class NormalizePriorityResult(BaseModel):
    issue_id: str
    priority: str          # the coerced, valid enum value that was written
    status: str            # always "triaged" on success
    coerced: bool          # True if the input priority was missing/invalid


def _coerce_priority(raw: Optional[str]) -> tuple[str, bool]:
    """Return (valid_enum_value, was_coerced)."""
    if raw is None:
        return DEFAULT_PRIORITY, True
    cleaned = raw.strip().lower()
    if cleaned in VALID_PRIORITIES:
        return cleaned, False
    return DEFAULT_PRIORITY, True


async def normalize_priority(ctx, data: NormalizePriorityInput) -> NormalizePriorityResult:
    pod = Pod.from_env()

    priority, coerced = _coerce_priority(data.priority)

    # Write only what triage produces; leave other fields untouched. repro_steps
    # and triage_reason are written only when the agent supplied them, so a re-run
    # never blanks them.
    patch: dict = {"priority": priority, "status": "triaged"}
    if data.repro_steps is not None:
        patch["repro_steps"] = data.repro_steps
    if data.reason is not None:
        patch["triage_reason"] = data.reason

    pod.table("issues").update(data.issue_id, patch)

    return NormalizePriorityResult(
        issue_id=data.issue_id,
        priority=priority,
        status="triaged",
        coerced=coerced,
    )
