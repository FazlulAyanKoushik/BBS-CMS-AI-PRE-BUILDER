# BBS-CMS AI Pre-Builder (PoC)

> **A modular, three-stage AI pipeline for generating website structure + content from Japanese business data.**

---

## 🎯 The Vision

Japanese SMEs need professional websites, but creating them requires:
1. **Understanding their business** (services, region, keywords) → *Agent 1*
2. **Writing relevant content** for each section → *Agent 2*
3. **Building the actual website** (HTML/CSS/React) → *Agent 3 (separate system)*

This system handles **Stages 1 & 2**. Stage 3 is a separate downstream system.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BBS-CMS AI Pre-Builder Pipeline                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   📄 Japanese Business CSV                                                  │
│        │                                                                    │
│        ▼                                                                    │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STAGE 1: AI AGENT 1 — Website Structure Architect                   │   │
│   │ (app/agents/agent1/)  ← CURRENT PHASE                               │   │
│   │ • Reads CSV + user criteria                                         │   │
│   │ • Decides: WHAT pages, WHAT sections, WHAT fields                   │   │
│   │ • Output: SiteSpec (JSON structure contract v1.0.0)                 │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│        │                                                                    │
│        ▼  SiteSpec Contract                                                 │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STAGE 2: AI AGENT 2 — Dynamic Content Generator                     │   │
│   │ (app/agents/agent2/)  ← PLANNED                                     │   │
│   │ • Input: CSV data + Agent 1 SiteSpec                                │   │
│   │ • Decides: ACTUAL CONTENT for each field (title, description, etc.) │   │
│   │ • Output: ContentSpec (JSON with filled content)                    │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│        │                                                                    │
│        ▼  ContentSpec                                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ STAGE 3: AI AGENT 3 — Website Builder (Separate System)             │   │
│   │ • Input: SiteSpec (structure) + ContentSpec (content)               │   │
│   │ • Builds: HTML, React, Vue, Next.js, WordPress, etc.                │   │
│   │ • Output: Deployable website                                        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 AI Agent 1 — The Structure Architect (Current)

**Role:** *Senior Web Strategy Architect*

Given a Japanese business CSV and user criteria, Agent 1 decides **what kind of website structure to build** — pages, sections, and fields — returning a `SiteSpec` JSON.

### What It Does

| Input | Processing | Output |
|-------|------------|--------|
| Japanese CSV (UTF-8/Shift-JIS) | Auto-detects encoding, normalizes 80+ columns | BusinessProfile |
| User Criteria (JSON) | Validates objectives, language, design hints | Criteria |
| | LLM Analysis (Gemini or Mock) | |
| | Falls back to deterministic mock if needed | |

### Output: `SiteSpec` (JSON Contract v1.0.0)

```json
{
  "summary": "One-paragraph site concept",
  "business_domain": "IT Consulting / Corporate Services",
  "target_region": "Tokyo, Japan",
  "language": "ja",
  "suggested_site_type": "company_website",
  "design_style": "Clean navy/white corporate design",
  "pages": [
    {
      "page_name": "top",
      "page_type": "standard",
      "purpose": "Hero + services overview + CTA",
      "sections": [
        {
          "section_type": "hero",
          "fields": [
            {"name": "title", "label": "Title"},
            {"name": "subtitle", "label": "Subtitle"}
          ]
        },
        {
          "section_type": "about",
          "fields": [
            {"name": "about_title", "label": "About Title"},
            {"name": "about_description", "label": "About Description"}
          ]
        }
      ]
    }
  ],
  "contract_version": "1.0.0"
}
```

> **Key Point:** Agent 1 defines the **schema** — field names, labels, types — but leaves content empty.

### Supported Site Types
- `company_website` — Corporate/Business services
- `portfolio` — Creative/agency showcases
- `ecommerce` — Online stores
- `restaurant_reservation` — Dining with booking
- `lp` — Landing pages
- `portal` — Multi-tenant platforms

---

## 🤖 AI Agent 2 — The Content Generator (Planned)

**Role:** *Copywriter / Content Strategist*

Agent 2 takes the **CSV business data** + **Agent 1's SiteSpec structure** and fills in **actual content** for every field.

### The Handoff

```
Agent 1 Output (SiteSpec):
  Section: "about"
  Fields: [about_title, about_description]

                    ▼ + CSV Data

Agent 2 Output (ContentSpec):
  Section: "about"
  Fields: [
    {name: "about_title", label: "About Title", content: "株式会社サンプルについて"},
    {name: "about_description", label: "About Description", 
     content: "当社は2010年設立のITコンサルティング企業です。..."}
  ]
```

### Agent 2 Interface (app/agents/agent2/agent.py)

```python
class BaseContentGenerator(ABC):
    @abstractmethod
    def generate(self, business_profile: dict, site_spec: SiteSpec) -> ContentSpec:
        """Generate dynamic content for each field in SiteSpec."""
        pass
```

### What Agent 2 Does NOT Do
- ❌ Generate HTML/CSS/React code
- ❌ Handle layout, styling, or responsive design
- ❌ Deploy or host websites

### What Agent 2 DOES Do
- ✅ Write compelling titles, descriptions, copy
- ✅ Use real business data from CSV (company name, services, region)
- ✅ Respect language, tone, and style preferences
- ✅ Output structured `ContentSpec` matching Agent 1's schema

---

## 🤖 AI Agent 3 — Website Builder (Separate System)

**Role:** *Frontend Engineer / Builder*

Completely separate system (not in this repo). Takes:
- **SiteSpec** (structure from Agent 1)
- **ContentSpec** (content from Agent 2)

And produces deployable websites in any format: HTML, React, Vue, Next.js, WordPress, etc.

---

## 🏗️ Architecture — Modular by Design

```
app/
├── agents/                 # AI Agents (separate packages)
│   ├── __init__.py         # Exports: AIAgent1, registry
│   ├── registry.py         # Agent factory for multi-agent orchestration
│   ├── agent1/             # AI_AGENT_1 — Structure Architect (CURRENT)
│   │   ├── agent.py        # AIAgent1 class
│   │   └── prompts.py      # System/user prompts
│   └── agent2/             # AI_AGENT_2 — Content Generator (PLANNED)
│       ├── agent.py        # BaseContentGenerator interface
│       └── __init__.py
├── api/                    # REST API layer
│   ├── router.py           # /api/generate, /api/health
│   └── __init__.py
├── contracts/              # Stable interfaces between agents
│   ├── site_spec.py        # SiteSpec v1.0.0 (Agent 1 output)
│   ├── content_spec.py     # ContentSpec v1.0.0 (Agent 2 output) — TBD
│   ├── version.py          # Contract versions
│   └── __init__.py
├── config/                 # Centralized settings
│   ├── settings.py         # Pydantic Settings (env-driven)
│   └── __init__.py
├── schemas/                # Pydantic models
│   └── __init__.py         # BusinessProfile, Criteria, SiteSpec, etc.
├── csv_loader.py           # Japanese CSV → BusinessProfile
├── llm.py                  # Provider abstraction (Gemini | Mock)
├── mock_site.py            # Deterministic offline spec builder
├── constants.py            # Japanese header → key mappings
└── main.py                 # FastAPI entrypoint (minimal)
```

### Why This Structure?

| Principle | Implementation |
|-----------|----------------|
| **Separation of Concerns** | Structure (Agent 1) ≠ Content (Agent 2) ≠ Build (Agent 3) |
| **Stable Contracts** | `app/contracts/` defines versioned interfaces |
| **Testability** | Mock provider for CI/CD, no API keys needed |
| **Extensibility** | Add agents via registry without touching others |
| **Team Independence** | Different teams own Agent 1, Agent 2, Agent 3 |

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env:
# LLM_PROVIDER=gemini     # or "mock" for no-key testing
# GEMINI_API_KEY=your_key # required if gemini
# GEMINI_MODEL=gemini-3.6-flash
```

### 3. Run the API
```bash
uv run uvicorn app.main:app --reload --port 8000
```

### 4. Test Endpoints
```bash
# Health check (shows active provider)
curl http://127.0.0.1:8000/api/health

# Generate site structure (Agent 1)
curl -X POST http://127.0.0.1:8000/api/generate \
  -F "file=@sample_inputs/infobix2_20260817191747.csv" \
  -F 'criteria_json={"objectives":"corporate website","language":"ja"}' \
  -F "row_index=0"
```

---

## 🖥️ CLI Usage

```bash
# Direct (in-process, uses .env for provider)
uv run python scripts/generate_site.py sample_inputs/infobix2_20260817191747.csv \
  --criteria '{"language":"ja"}' \
  --output spec.json

# Via API server
uv run python scripts/generate_site.py sample_inputs/infobix2_20260817191747.csv \
  --api http://127.0.0.1:8000 \
  --output spec.json
```

---

## 🔧 Configuration

All settings in `.env` (loaded via `app/config/settings.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `mock` | `gemini` or `mock` |
| `GEMINI_API_KEY` | — | Required if `LLM_PROVIDER=gemini` |
| `GEMINI_MODEL` | `gemini-3.6-flash` | Model to use |
| `HOST` | `127.0.0.1` | Server host |
| `PORT` | `8000` | Server port |
| `MAX_CSV_BYTES` | `10485760` | 10 MB upload limit |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## 📊 Startup Logging

On startup, the system logs complete configuration:

```
============================================================
🚀 BBS-CMS AI Pre-Builder v0.1.0 starting up
============================================================
📡 LLM Provider Configuration:
   Provider:      GEMINI
   Configured:    GEMINI
   API Key:       ✅ Provided
   API Key (masked): AQ.Ab8RN6K...XBEg
   Model:         gemini-3.6-flash
🌐 Server Configuration:
   Host:          127.0.0.1
   Port:          8000
   Reload:        Enabled
📄 CSV Processing:
   Max Size:      10 MB
   Encodings:     utf-8-sig, utf-8, cp932, shift_jis, latin-1
📋 Contract:
   Version:       1.0.0
============================================================
✅ Startup complete - ready to accept requests
============================================================
```

### Request Logging (Middleware)
Every request is logged with timing:
```
📥 POST /api/generate from 127.0.0.1
📤 POST /api/generate → 200 ✅ (1234.56ms)
```

---

## 🧪 Testing

```bash
# All tests (uses mock provider, no API key needed)
uv run pytest tests/ -v

# Test specific functionality
uv run pytest tests/test_core.py::test_agent_mock_produces_valid_spec -v
```

---

## 📁 Sample Data

`sample_inputs/infobix2_20260817191747.csv` — Japanese business CSV template (header only, no data rows tolerated)

---

## 🔮 Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **Agent 1: Structure** | ✅ Done | CSV + Criteria → SiteSpec JSON |
| **Contracts** | ✅ Done | Versioned SiteSpec v1.0.0 |
| **Agent 2: Content** | 🔄 Planned | CSV + SiteSpec → ContentSpec |
| **Agent 3: Build** | 📦 Separate | SiteSpec + ContentSpec → Website |
| **Multi-tenant API** | 💡 Future | Team workspaces, versioning |

---

## 🤝 Contributing

1. **Agent 1 changes** → Work in `app/agents/agent1/`
2. **Agent 2 implementation** → Implement `BaseContentGenerator` in `app/agents/agent2/`
3. **Contract changes** → Update `app/contracts/` (major version = breaking)
4. **Tests** → Add to `tests/` for any new functionality

---

## 📄 License

MIT License — See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- **Google Gemini** for LLM capabilities
- **FastAPI** for the API framework
- **Pydantic** for type-safe settings and schemas
- **Japanese business community** for CSV format standards