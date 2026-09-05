# BBS-CMS AI Pre-Builder (PoC)

Takes a Japanese business CSV (e.g. `sample_inputs/infobix2_20260817191747.csv`)
plus user website criteria, and uses an AI agent (`AI_AGENT_1`) to decide what
kind of website should be built — returning a **website structure spec as JSON**.

**Scope:** REST API output only. No database, no HTML/frontend generation.

## Setup

```bash
uv sync            # create .venv + install dependencies
```

Copy `.env.example` to `.env` if you want to change the LLM provider.

- Default provider is `mock` — deterministic output, no API key required.
- Set `LLM_PROVIDER=gemini` (plus your `GEMINI_API_KEY`) to use Gemini.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

Endpoints:

| Method | Path           | Description                                                         |
|--------|----------------|---------------------------------------------------------------------|
| GET    | `/api/health`  | Health check                                                        |
| POST   | `/api/generate`| Upload CSV + criteria JSON → site structure spec (JSON response)    |

### Example request

```bash
curl -X POST http://127.0.0.1:8000/api/generate \
  -F "file=@sample_inputs/infobix2_20260817191747.csv" \
  -F "criteria_json={\"objectives\":\"corporate website\",\"language\":\"ja\"}" \
  -F "row_index=0"
```

Interactive docs: `http://127.0.0.1:8000/docs`.

## Run without the server (CLI)

```bash
# Direct (in-process, mock or openai per env)
uv run python scripts/generate_site.py sample_inputs/infobix2_20260817191747.csv \
  --criteria '{"objectives":"IT company website","language":"ja"}'

# Via the API
uv run python scripts/generate_site.py sample_inputs/infobix2_20260817191747.csv \
  --api http://127.0.0.1:8000 --output spec.json
```

## Architecture

- `app/csv_loader.py` — UTF-8 / Shift-JIS auto-detect, normalize rows → business profile
- `app/agent.py` — `AI_AGENT_1` orchestration (profile + criteria → `SiteSpec`)
- `app/llm.py` — provider wrapper (`gemini` | `mock` fallback)
- `app/prompts.py` — system/user prompts for the agent
- `app/mock_site.py` — deterministic offline site-spec builder
- `app/schemas.py` — Pydantic models for the API
- `app/main.py` — FastAPI entrypoint