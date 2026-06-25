"""Single source of truth for connecting to the Lemma pod.

Every script and Function goes through ``get_pod()`` so the connection logic
(env loading, auth resolution) lives in exactly one place.

Auth resolution (handled by the SDK's ``Pod.from_env``):
  1. ``LEMMA_TOKEN`` env var, else
  2. a CLI session in ``~/.lemma/config.json`` (written by ``lemma auth login``).
``LEMMA_POD_ID`` selects the pod; ``LEMMA_BASE_URL`` defaults to
https://api.lemma.work.
"""

from __future__ import annotations

import pathlib

from dotenv import load_dotenv
from lemma_sdk import Pod

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_env() -> None:
    """Load ``.env`` from the repo root into the process environment (no-op if absent)."""
    load_dotenv(REPO_ROOT / ".env")


def get_pod() -> Pod:
    """Return a connected pod, reading credentials from ``.env`` / CLI session.

    Raises ``LemmaConfigError`` / ``ValueError`` with an actionable message if no
    pod id or token can be resolved.
    """
    load_env()
    return Pod.from_env()
