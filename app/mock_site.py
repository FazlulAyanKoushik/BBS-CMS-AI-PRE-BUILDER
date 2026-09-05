"""Deterministic mock site-spec builder used when no LLM key is configured."""

from __future__ import annotations

from typing import Any

from app.schemas import SitePage, SiteSpec


def _page(name: str, sections: list[dict[str, Any]]) -> SitePage:
    return SitePage(
        page_name=name,
        page_type="standard",
        purpose=f"{name} page for the business",
        sections=sections,
    )


def _hero() -> dict[str, Any]:
    return {
        "section_type": "hero",
        "heading": "Main image section",
        "fields": [
            {"name": "title", "label": "Title"},
            {"name": "subtitle", "label": "Subtitle"},
        ],
    }


def _about() -> dict[str, Any]:
    return {
        "section_type": "about",
        "heading": "About section",
        "fields": [
            {"name": "about_title", "label": "About Title"},
            {"name": "about_description", "label": "About description"},
        ],
    }


def _carousel() -> dict[str, Any]:
    return {
        "section_type": "carousel",
        "heading": "Carousel section",
        "fields": [{"name": "slides", "label": "Carousel slides"}],
    }


def _service_detail(service_name: str) -> dict[str, Any]:
    return {
        "section_type": "service_detail",
        "heading": service_name,
        "fields": [
            {"name": "service_name", "label": "Service name", "content": service_name},
            {"name": "description", "label": "Description"},
        ],
    }


def _contact_cta() -> dict[str, Any]:
    return {
        "section_type": "contact",
        "heading": "Contact / CTA",
        "fields": [
            {"name": "phone", "label": "Phone"},
            {"name": "address", "label": "Address"},
        ],
    }


def build_mock_spec(business_profile: dict[str, Any], criteria: dict[str, Any]) -> dict[str, Any]:
    """Build a structural site spec from the profile + criteria (content fields empty)."""
    business_type = business_profile.get("business_type") or "general business"
    business_domain = business_profile.get("services") or business_profile.get("keywords") or [business_type]
    language = criteria.get("language") or business_profile.get("region", {}).get("language_selection") or "ja"
    region = business_profile.get("region", {})
    target_region = " / ".join(
        p for p in [region.get("prefecture"), region.get("city")] if p
    ) or "Japan"

    services = business_profile.get("services") or [business_type]
    store_name = (
        business_profile.get("store_name")
        or business_profile.get("business_account_name")
        or "the business"
    )
    objectives = criteria.get("objectives")

    top_page = _page(
        "top",
        [
            _hero(),
            _about(),
            {"section_type": "services_overview", "heading": "Services overview", "fields": [{"name": "service_summary", "label": "Service summary"}]},
            _contact_cta(),
        ],
    )
    service_page = _page(
        "service",
        [_carousel()] + [_service_detail(s) for s in services],
    )
    company_page = _page(
        "company",
        [
            {"section_type": "company_overview", "heading": "Company profile", "fields": [{"name": "company_name", "label": "Company name"}, {"name": "history", "label": "History"}]},
            {"section_type": "access", "heading": "Access", "fields": [{"name": "address", "label": "Address"}, {"name": "hours", "label": "Business hours"}]},
        ],
    )
    contact_page = _page(
        "contact",
        [
            {"section_type": "contact_form", "heading": "Contact form", "fields": [{"name": "form_message", "label": "Message"}]},
            {"section_type": "map", "heading": "Map", "fields": [{"name": "map_embed", "label": "Map embed"}]},
        ],
    )

    pages: list[Any] = [top_page, service_page, company_page, contact_page]

    spec = SiteSpec(
        summary=(
            f"{business_type} site for {store_name} in {target_region}, "
            f"targeting visitors of {', '.join(business_domain[:2])}."
            + (f" Goal: {objectives}." if objectives else "")
        ),
        business_domain=" / ".join(business_domain[:4]) or business_type,
        target_region=target_region,
        language=language,
        suggested_site_type="company_website",
        design_style=criteria.get("design_style"),
        pages=pages,
    )
    return spec.model_dump(exclude_none=True)