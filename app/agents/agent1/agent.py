"""AI_AGENT_1: orchestrates business understanding -> website structure spec."""

from __future__ import annotations

import logging
from typing import Any

from app.llm import MockProvider, get_provider
from app.schemas import SiteSpec
from app.agents.agent1.prompts import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

AGENT_NAME = "AI_AGENT_1"


class AIAgent1:
    """Main agent. Understands the business domain/requirements/region and
    decides what kind of website to build, returning a SiteSpec."""

    name = AGENT_NAME

    def __init__(self, provider=None) -> None:
        self.provider = provider or get_provider()

    @property
    def provider_name(self) -> str:
        return self.provider.name

    def generate(self, business_profile: dict[str, Any], criteria: dict[str, Any] | None = None) -> SiteSpec:
        criteria = criteria or {}
        logger.info("AI_AGENT_1 generating site spec using provider=%s", self.provider.name)
        raw = self.provider.generate_structured_spec(business_profile, criteria)
        return self._validate(raw, business_profile, criteria)

    @staticmethod
    def _validate(raw: dict[str, Any], profile: dict[str, Any], criteria: dict[str, Any]) -> SiteSpec:
        """Coerce provider output into a clean SiteSpec, falling back to mock."""
        try:
            return SiteSpec.model_validate(raw)
        except Exception as exc:  # validation / schema mismatch -> deterministic fallback
            logger.warning("Provider output failed SiteSpec validation (%s). Falling back to mock.", exc)
            fallback = MockProvider().generate_structured_spec(profile, criteria)
            return SiteSpec.model_validate(fallback)


def run_agent(business_profile: dict[str, Any], criteria: dict[str, Any] | None = None) -> tuple[SiteSpec, str]:
    agent = AIAgent1()
    spec = agent.generate(business_profile, criteria)
    return spec, agent.provider_name