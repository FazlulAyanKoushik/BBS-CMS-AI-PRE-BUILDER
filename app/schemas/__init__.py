"""Pydantic models for the REST API.

This package contains all schema definitions organized by domain:
- business: BusinessProfile, Criteria
- site_spec: SiteSpec, SitePage, SiteSection, SiteSectionField
- response: GenerateResponse, GenerateResponseDict, HealthResponse
"""

from __future__ import annotations

from app.schemas.business import BusinessProfile, Criteria
from app.schemas.response import GenerateResponse, GenerateResponseDict, HealthResponse
from app.schemas.site_spec import SiteSpec, SitePage, SiteSection, SiteSectionField

__all__ = [
    # Business
    "BusinessProfile",
    "Criteria",
    # Site Spec
    "SiteSpec",
    "SitePage",
    "SiteSection",
    "SiteSectionField",
    # Responses
    "GenerateResponse",
    "GenerateResponseDict",
    "HealthResponse",
]