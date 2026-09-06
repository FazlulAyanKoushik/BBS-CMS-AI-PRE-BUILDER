"""Site specification Pydantic models."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.contracts.version import CONTRACT_VERSION


class SiteSectionField(BaseModel):
    name: str
    label: Optional[str] = None
    content: Optional[str] = None


class SiteSection(BaseModel):
    section_type: str = "generic"
    heading: Optional[str] = None
    description: Optional[str] = None
    fields: list[SiteSectionField] = Field(default_factory=list)


class SitePage(BaseModel):
    page_name: str
    page_type: str = "standard"
    purpose: Optional[str] = None
    sections: list[SiteSection] = Field(default_factory=list)


class SiteSpec(BaseModel):
    """The AI-generated website structure spec (JSON output, no HTML)."""

    summary: str
    business_domain: str
    target_region: str
    language: str
    suggested_site_type: str
    design_style: Optional[str] = None
    pages: list[SitePage] = Field(default_factory=list)
    contract_version: str = CONTRACT_VERSION