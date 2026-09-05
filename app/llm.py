"""Pluggable LLM provider: Google Gemini (native SDK) with a deterministic mock fallback."""

from __future__ import annotations

import abc
import os
from typing import Any, Literal

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai import types as genai_types
except Exception:  # pragma: no cover - google-genai optional
    genai = None  # type: ignore[assignment]
    genai_types = None  # type: ignore[assignment]

from app.mock_site import build_mock_spec
from app.prompts import SYSTEM_PROMPT, build_user_prompt

DEFAULT_MODEL = os.getenv("GEMINI_MODEL") or "gemini-3.6-flash"


class LLMProvider(abc.ABC):
    name = "base"

    @abc.abstractmethod
    def generate_structured_spec(self, business_profile: dict[str, Any], criteria: dict[str, Any]) -> dict[str, Any]:
        """Return a parsed site-spec dict (see SiteSpec schema)."""


class MockProvider(LLMProvider):
    """Deterministic offline provider — used when no API key is set."""

    name = "mock"

    def generate_structured_spec(self, business_profile: dict[str, Any], criteria: dict[str, Any]) -> dict[str, Any]:
        return build_mock_spec(business_profile, criteria)


class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        if genai is None:
            raise ImportError("The 'google-genai' package is not installed.")
        self.model = model or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))

    def generate_structured_spec(self, business_profile: dict[str, Any], criteria: dict[str, Any]) -> dict[str, Any]:
        user_prompt = build_user_prompt(business_profile, criteria)
        response = self.client.models.generate_content(
            model=self.model,
            contents=[SYSTEM_PROMPT, user_prompt],
            config=genai_types.GenerateContentConfig(response_mime_type="application/json"),
        )
        content = getattr(response, "text", None) or ""
        return _parse_json_object(content)


def _parse_json_object(content: str) -> dict[str, Any]:
    """Robustly parse the model's JSON output."""
    import json
    import re

    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    match = re.search(r"{.*}", content, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass
    raise ValueError(f"LLM output was not valid JSON:\n{content[:500]}")


def get_provider() -> LLMProvider:
    """Instantiate the configured provider (env: LLM_PROVIDER=gemini|mock)."""
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    if provider == "gemini":
        return GeminiProvider()
    return MockProvider()


def provider_name() -> Literal["gemini", "mock"]:
    name = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    return "gemini" if name == "gemini" else "mock"