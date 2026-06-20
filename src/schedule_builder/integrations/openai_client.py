"""OpenAI client wrapper for scope analysis."""

from __future__ import annotations

from openai import OpenAI  # type: ignore[import-untyped]

from schedule_builder.config.settings import settings
from schedule_builder.core.exceptions import ServiceUnavailableError


class OpenAIClient:
    provider_name = "openai"

    def __init__(self, api_key: str | None = None, model_name: str | None = None) -> None:
        self.model_name = model_name or settings.openai_model
        self._api_key = api_key or settings.openai_api_key
        self._client = OpenAI(api_key=self._api_key) if self._api_key else None

    def analyze(self, *, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            raise ServiceUnavailableError(message="OpenAI API key is not configured")

        response = self._client.responses.create(
            model=self.model_name,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.output_text
