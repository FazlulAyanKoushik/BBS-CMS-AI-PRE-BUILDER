"""Business-related Pydantic models."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class BusinessProfile(BaseModel):
    """Normalized business information extracted from the CSV."""

    model_config = ConfigDict(extra="allow")

    store_name: Optional[str] = None
    business_type: Optional[str] = None
    phone: Optional[str] = None
    website_url: Optional[str] = None
    address: Optional[str] = None
    keywords: list[str] = Field(default_factory=list)
    services: list[str] = Field(default_factory=list)
    region: dict[str, Any] = Field(default_factory=dict)
    business_hours: Optional[str] = None
    opening_date: Optional[str] = None
    employees: Optional[str] = None
    attributes: dict[str, str] = Field(default_factory=dict)


class Criteria(BaseModel):
    """User-provided criteria about the website to build."""

    model_config = ConfigDict(extra="allow")

    objectives: Optional[str] = None
    design_style: Optional[str] = None
    language: Optional[str] = None
    page_hints: Optional[str] = None
    notes: Optional[str] = None