"""API Router for BBS-CMS AI Pre-Builder.

Contains all API endpoints. Currently only /api/generate for AI_AGENT_1.
Future endpoints for AI_AGENT_2 can be added here.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.agents import AIAgent1, AGENT_NAME
from app.csv_loader import build_profile
from app.llm import provider_name
from app.schemas import GenerateResponseDict, HealthResponse
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/api/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(provider=provider_name())


@router.post("/api/generate", response_model=GenerateResponseDict, tags=["generate"])
async def generate(
    file: UploadFile = File(
        ...,
        description="Japanese business CSV (UTF-8 or Shift-JIS). Headers row optional.",
    ),
    criteria_json: str = Form(
        "{}",
        description="JSON string with user website criteria, e.g. {\"objectives\": \"...\", \"language\": \"ja\"}",
    ),
    row_index: int = Form(0, ge=0, description="Which data row of the CSV to use (0-based)."),
) -> dict[str, Any]:
    """Generate a website structure spec from a business CSV and criteria.
    
    Uses AI_AGENT_1 to analyze the business profile and return a SiteSpec.
    """
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(data) > settings.max_csv_bytes:
        raise HTTPException(status_code=413, detail="CSV too large (max 10 MB).")

    try:
        criteria = json.loads(criteria_json) if criteria_json and criteria_json.strip() else {}
        if not isinstance(criteria, dict):
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(status_code=422, detail="criteria_json must be a valid JSON object.")

    try:
        profile = build_profile(data, row_index=row_index)
    except IndexError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    agent = AIAgent1()
    try:
        spec = agent.generate(profile, criteria)
    except Exception as exc:
        logger.exception("AI_AGENT_1 generation failed")
        raise HTTPException(status_code=500, detail=f"AI_AGENT_1 failed: {exc}")

    return GenerateResponseDict(
        agent_name=AGENT_NAME,
        provider=agent.provider_name,
        site_spec=spec.model_dump(exclude_none=True),
    ).model_dump()


# Future: AI_AGENT_2 endpoints can be added here
# @router.post("/api/generate-content", ...)
# async def generate_content(...):
#     pass