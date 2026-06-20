"""Helpers for loading prompt templates from the repository."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from schedule_builder.core.exceptions import ServiceUnavailableError

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPT_DIR = REPO_ROOT / "data" / "prompts"


@lru_cache(maxsize=None)
def load_prompt(prompt_filename: str) -> str:
    prompt_path = PROMPT_DIR / prompt_filename
    if not prompt_path.exists():
        raise ServiceUnavailableError(
            message="Prompt template is not available",
            details={"prompt_filename": prompt_filename},
        )
    return prompt_path.read_text(encoding="utf-8").strip()
