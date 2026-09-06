"""FastAPI entrypoint for the BBS-CMS AI Pre-Builder PoC.

REST API only — no database, no HTML output. The API ingests a Japanese
business CSV + criteria and returns a website structure spec as JSON.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import logging

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI

from app.api import router
from app.config import settings
from app.llm import get_provider
from app.middleware import RateLimitMiddleware, RequestLoggingMiddleware

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app - logs configuration on startup."""
    # ─── Startup ──────────────────────────────────────────────────────────────
    provider = get_provider()

    logger.info("=" * 60)
    logger.info("🚀 %s v%s starting up", settings.app_name, settings.app_version)
    logger.info("=" * 60)

    # LLM Provider info
    logger.info("📡 LLM Provider Configuration:")
    logger.info("   Provider:      %s", provider.name.upper())
    logger.info("   Configured:    %s", settings.llm_provider.upper())

    if settings.llm_provider == "gemini":
        api_key_status = "✅ Provided" if settings.gemini_api_key else "❌ Missing (will fallback to mock)"
        logger.info("   API Key:       %s", api_key_status)
        if settings.gemini_api_key:
            # Show only first 10 chars for security
            masked_key = settings.gemini_api_key[:10] + "..." + settings.gemini_api_key[-4:] if len(settings.gemini_api_key) > 14 else "***"
            logger.info("   API Key (masked): %s", masked_key)
        logger.info("   Model:         %s", settings.gemini_model)
    else:
        logger.info("   Mode:          Deterministic mock (no API key required)")

    # Server info
    logger.info("🌐 Server Configuration:")
    logger.info("   Host:          %s", settings.host)
    logger.info("   Port:          %d", settings.port)
    logger.info("   Reload:        %s", "Enabled" if settings.reload else "Disabled")

    # CSV Processing
    logger.info("📄 CSV Processing:")
    logger.info("   Max Size:      %s MB", settings.max_csv_bytes // (1024 * 1024))
    logger.info("   Encodings:     %s", ", ".join(settings.supported_encodings))

    # Contract
    logger.info("📋 Contract:")
    logger.info("   Version:       %s", settings.contract_version)

    logger.info("=" * 60)
    logger.info("✅ Startup complete - ready to accept requests")
    logger.info("=" * 60)

    yield

    # ─── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("🛑 %s shutting down", settings.app_name)
    logger.info("=" * 60)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Ingests a Japanese business CSV + criteria and returns a website structure spec JSON via AI_AGENT_1.",
    lifespan=lifespan,
)

# Add rate limiting middleware (first, so it runs before request logging)
app.add_middleware(RateLimitMiddleware)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware, logger=logger)

app.include_router(router)