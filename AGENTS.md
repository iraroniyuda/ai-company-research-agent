# AGENTS.md

Project: AI Company Research Agent

Purpose:
Build a small AI-powered company research system for the Jackson Ventures AI Agentic Platform Engineer test.

Working rules for the coding agent:
- Keep changes minimal and focused
- Do not change unrelated files
- Prefer simple, readable implementations over overengineering
- Reuse the existing database, model, and API structure whenever possible
- Show the plan before editing files
- Preserve safe rerun behavior for scripts
- Keep scripts easy to demo from the command line
- Avoid hardcoded fallback datasets in the final collection flow
- Use real collected data for the final Step 1 path
- Do not change routes, analyzer logic, or collector logic unless explicitly requested
- Keep output structured and easy to verify
- Preserve fallback-safe behavior for AI analysis
- When debugging, isolate the issue first before refactoring broadly

Project-specific expectations:
- Collection should store:
  - company_name
  - website (if available)
  - description
- Enrichment should fill:
  - industry
  - business_model
  - summary
  - use_case
- API endpoints should remain:
  - GET /companies
  - GET /companies/{id}

Coding style:
- Keep functions small and purpose-specific
- Prefer explicit names over clever abstractions
- Avoid adding new dependencies unless clearly helpful
- Preserve compatibility with Windows CMD commands used in the README

Operational notes:
- SQLite is the primary local database for this take-home project
- Gemini free-tier limits may require rerunning enrichment later
- Partial progress should be preserved where possible
