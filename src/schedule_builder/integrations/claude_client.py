"""Claude API client wrapper for scope analysis."""

from __future__ import annotations

from typing import Protocol

from anthropic import Anthropic  # type: ignore[import-untyped]

from schedule_builder.config.settings import settings
from schedule_builder.core.exceptions import ServiceUnavailableError


class ScopeAnalysisClient(Protocol):
    provider_name: str
    model_name: str

    def analyze(self, *, system_prompt: str, user_prompt: str) -> str: ...


class ClaudeClient:
    provider_name = "claude"

    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.anthropic_model
        self._api_key = api_key or settings.anthropic_api_key
        self._client = Anthropic(api_key=self._api_key) if self._api_key else None

    def analyze(self, *, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            raise ServiceUnavailableError(message="Anthropic API key is not configured")

        message = self._client.messages.create(
            model=self.model_name,
            max_tokens=2048,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return "".join(block.text for block in message.content if hasattr(block, "text"))
