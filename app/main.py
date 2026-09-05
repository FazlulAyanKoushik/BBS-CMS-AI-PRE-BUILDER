"""FastAPI entrypoint for the BBS-CMS AI Pre-Builder PoC.

REST API only — no database, no HTML output. The API ingests a Japanese
business CSV + criteria and returns a website structure spec as JSON.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from dotenv import load_dotenv

from app.agent import AGENT_NAME, AIAgent1
from app.csv_loader import build_profile
from app.llm import provider_name
from app.schemas import GenerateResponseDict, HealthResponse

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="BBS-CMS AI Pre-Builder (PoC)",
    version="0.1.0",
    description="Ingests a Japanese business CSV + criteria and returns a website structure spec JSON via AI_AGENT_1.",
)

_MAX_CSV_BYTES = 10 * 1024 * 1024


@app.get("/api/health", response_model=HealthResponse, tags=["meta"])
def health() -> HealthResponse:
    return HealthResponse(provider=provider_name())


@app.post("/api/generate", response_model=GenerateResponseDict, tags=["generate"])
async def generate(
    file: UploadFile = File(
        ...,
        description="Japanese business CSV (UTF-8 or Shift-JIS). Headers row optional.",
    ),
    criteria_json: str = Form(
        "{ }",
        description="JSON string with user website criteria, e.g. {\"objectives\": \"...\", \"language\": \"ja\"}",
    ),
    row_index: int = Form(0, ge=0, description="Which data row of the CSV to use (0-based)."),
) -> dict[str, Any]:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(data) > _MAX_CSV_BYTES:
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
        raise HTTPException(status_code=500, detail=f"AI_AGENT_1 failed: {exc}")

    return GenerateResponseDict(
        agent_name=AGENT_NAME,
        provider=agent.provider_name,
        site_spec=spec.model_dump(exclude_none=True),
    ).model_dump()