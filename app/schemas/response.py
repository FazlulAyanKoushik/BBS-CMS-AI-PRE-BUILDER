"""API response Pydantic models."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel

from app.schemas.site_spec import SiteSpec


class GenerateResponse(BaseModel):
    agent_name: str = "AI_AGENT_1"
    provider: str = "mock"
    site_spec: SiteSpec


class GenerateResponseDict(BaseModel):
    agent_name: str = "AI_AGENT_1"
    provider: str = "mock"
    site_spec: dict[str, Any]


class HealthResponse(BaseModel):
    status: str = "ok"
    agent: str = "AI_AGENT_1"
    provider: Literal["gemini", "mock"] = "mock"