# AI Company Research Agent

A small AI-powered company research system built for the Jackson Ventures AI Agentic Platform Engineer test.

This project collects real company data from a public source, enriches each company with AI-generated insights, stores the results in SQLite, and exposes the data through a REST API. The goal is not to build a production-ready system, but to demonstrate clear system design, practical backend implementation, structured AI usage, and effective agentic workflow with a coding agent.

## What the system does

The system performs four core steps:

1. Collects real company data from a public source
2. Uses an AI analyzer to generate structured company insights
3. Stores both raw and enriched data in a database
4. Exposes the results through a REST API

The enriched fields are:

- `industry`
- `business_model`
- `summary`
- `use_case`

## Brief alignment

This project was built to match the core requirements of the test:

- collect at least 10 companies
- store `company_name`, `website` if available, and `description`
- analyze each company with AI
- store the AI-generated outputs
- expose the results through API endpoints

Implemented endpoints:

- `GET /companies`
- `GET /companies/{id}`

This repository is also intended to include:

- source code
- README
- Codex workflow transcript/log
- `AGENTS.md`

## Tech stack

- Python 3.12
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Google Gemini API (`google-genai`)
- Requests
- BeautifulSoup4
- Codex CLI

## Architecture overview

The project is intentionally small and simple.

### `scripts/collect_companies.py`

- collects real company data from a public source
- extracts `company_name`, `website` when available, and `description`
- inserts up to 10 companies into SQLite
- skips duplicates safely

### `scripts/enrich_companies.py`

- finds companies whose AI fields are still missing
- checks SQLite-backed analysis cache before making a model call
- calls the analyzer only on cache misses
- updates:
  - `industry`
  - `business_model`
  - `summary`
  - `use_case`
- commits per company so partial progress is preserved if rate limits or failures occur

### `app/services/analyzer.py`

- sends company descriptions to Gemini
- requests structured JSON output
- validates the output with Pydantic
- returns a safe fallback object when input is blank or the model call fails

### `app/api/routes/companies.py`

- exposes stored data through REST endpoints
- supports optional filtering and search on `GET /companies`

### `app/core/database.py`

- configures SQLite
- manages SQLAlchemy engine/session setup
- creates tables

## Project structure

```text
ai-company-research-agent/
  app/
    api/
      routes/
        companies.py
    core/
      config.py
      database.py
    models/
      analysis_cache.py
      company.py
    schemas/
      company.py
    services/
      analyzer.py
      repository.py
    main.py
  scripts/
    collect_companies.py
    enrich_companies.py
    seed_companies.py
  data/
  tests/
  AGENTS.md
  README.md
  requirements.txt
  .env.example
```

## Data source

The final collection flow uses real scraped company data from a public Y Combinator company directory page.

Notes:

- `website` is stored only when it is clearly available from the scraped source
- `website` may legitimately remain `null` for some rows
- the collector is intentionally narrow and tuned to one public page for this take-home implementation

## Note on bootstrapping

A temporary seed script (`scripts/seed_companies.py`) was used earlier during development to validate the database and API flow quickly.

That script is not the final Step 1 collection path.

The final collection path is:

```bat
python -m scripts.collect_companies
```

## Setup

### 1. Create and activate the virtual environment

Windows CMD:

```bat
py -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bat
python -m pip install -r requirements.txt
```

### 3. Create `.env`

Copy `.env.example` to `.env`, then set your Gemini API key.

Example:

```env
GEMINI_API_KEY=your_key_here
DATABASE_URL=sqlite:///./companies.db
```

## How to run

### Step 1: collect real companies

```bat
python -m scripts.collect_companies
```

Expected output pattern:

```text
fetched 10
inserted 10
skipped 0
```

### Step 2: enrich companies with AI

```bat
python -m scripts.enrich_companies
```

This script is safe to rerun. It only processes companies whose AI-generated fields are still missing.

Because the project uses Gemini free tier during development, rate limits may interrupt enrichment. In that case, rerun the script later. The script commits incrementally, so previous progress is preserved.

### Step 3: start the API

```bat
python -m uvicorn app.main:app --reload
```

API base URL:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## API endpoints

### `GET /companies`

Returns all companies with collected fields and AI-generated insights.

Supports optional query parameters:

- `industry` for exact industry filtering
- `search` for case-insensitive matching across `company_name`, `description`, `industry`, and `summary`

Example response:

```json
[
  {
    "id": 1,
    "company_name": "Example Company",
    "website": "https://example.com",
    "description": "Example description",
    "industry": "Developer Tools",
    "business_model": "SaaS",
    "summary": "Short summary",
    "use_case": "Potential use case"
  }
]
```

### `GET /companies/{id}`

Returns one company by ID.

## How the AI analyzer works

The analyzer receives a company description and asks the model to return structured JSON with exactly these fields:

- `industry`
- `business_model`
- `summary`
- `use_case`

The output is validated with Pydantic before being accepted.

Safety behavior:

- if the description is blank, it returns null fields
- if the model call fails, it returns null fields
- if parsing or validation fails, it returns null fields

This makes the enrichment step safer and easier to rerun.

## Bonus improvements

This project includes two small optional improvements:

- simple filtering and search support on `GET /companies` via `industry` and `search` query params
- SQLite-backed caching of AI analysis results by exact company description to avoid redundant model calls

The cache only stores non-empty analysis results, so failed or all-null fallback outputs are not persisted as valid cached data.

## Agentic tool usage

This project was built with Codex CLI as the primary agentic coding tool.

Codex was used for:

- scaffolding the project structure
- generating database/model/schema layers
- iterating on API routes
- implementing the seed, collector, and enrichment scripts
- revising the analyzer from OpenAI to Gemini
- debugging scraper issues
- refining extraction logic for clean company names
- adjusting enrichment behavior for rate-limit-safe reruns
- adding filtering/search and SQLite-backed analysis caching as bonus improvements

Human review was applied throughout, including:

- rejecting brittle or hardcoded collection approaches
- correcting optional website handling
- switching away from OpenAI after quota issues
- debugging Gemini response handling
- tightening collector extraction after malformed names and duplicate logical companies appeared

## Design decisions

### Why SQLite

SQLite was chosen because it is the simplest database option for a small take-home project.

### Why a real collector instead of only seed data

A temporary seed script helped bootstrap the flow early, but the final Step 1 path uses real collected company data from a public source to better match the assignment.

### Why Gemini instead of OpenAI in the final analyzer

The project initially used OpenAI, but that path was blocked by API quota limitations during development. The analyzer was then migrated to Gemini so the system could continue using a real LLM integration.

### Why enrichment is rerunnable

Free-tier API usage can hit rate limits. Instead of making enrichment all-or-nothing, the script commits progress incrementally so the process can be resumed safely.

### Why SQLite-backed caching

The project hit real Gemini free-tier rate limits during development. SQLite-backed caching by exact description reduces redundant model calls and makes reruns more efficient without adding extra infrastructure.

## Assumptions

- collecting up to 10 companies is enough for this take-home implementation
- `website` may remain null if it is not clearly exposed in the scraped source
- enrichment quality depends on free-tier model behavior and output consistency
- the project prioritizes clarity and traceability over heavy abstraction

## Limitations

- website extraction depends on what is clearly exposed in the source HTML
- some records may legitimately keep `website = null`
- Gemini free-tier rate limits can interrupt enrichment and require reruns
- the collector is intentionally tuned to a specific public source rather than being a general-purpose crawler
- the system is not production-grade and does not include auth, migrations, job queues, or retry orchestration

## Deliverables included

This repository is intended to include:

- source code
- README
- Codex workflow transcript/log
- `AGENTS.md`
