# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the project

```bash
# 1. Start Ollama (run once, keep terminal open)
ollama serve
ollama pull nemotron-mini      # ~2.7 GB — NVIDIA's official Ollama model
# or for immediate testing (already downloaded):
# ollama pull llama3.2

# 2. Start FastAPI backend (from project root)
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
# → http://localhost:8000/api/health

# 3. Start Next.js frontend (separate terminal)
cd frontend && npm run dev
# → http://localhost:3000

# 4. Generate model comparison charts (no GPU needed)
python -m backend.fine_tuning.compare_models --demo
# Charts saved to static/charts/ → visible at /analytics page

# 5. (Optional) Generate fine-tuning dataset
python -m backend.fine_tuning.generate_dataset

# 6. (Optional, GPU required) Run LoRA fine-tuning
python -m backend.fine_tuning.train_lora
```

## Architecture

**Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind CSS + Framer Motion  
**Backend**: FastAPI + SQLAlchemy (async) + Ollama  
**Database**: PostgreSQL (Neon cloud, `DATABASE_URL` in `backend/.env`)  
**Vector DB**: ChromaDB (auto-seeded with skill resources on startup)  
**Analytics**: PostHog (`NEXT_PUBLIC_POSTHOG_KEY` in `frontend/.env.local`)

### 4-Model Architecture
Each task uses a specialized model via `backend/services/llm.py`:
| Task | Model | Function |
|------|-------|----------|
| Roadmap generation | NVIDIA Nemotron Ultra 253B (main + fine-tuned) | `call_nemotron()` |
| Skill extraction from PDF | Mistral 7B Instruct | `call_mistral()` |
| Market insight + RAG | Meta Llama 3.3 70B | `call_llama70b()` |
| Interview & quiz questions | Qwen 2.5 72B | `call_qwen()` |

Fallback chain for every model: OpenRouter → local Ollama (nemotron-mini/llama3.2).

Model IDs are set in `backend/.env`: `OPENROUTER_MODEL`, `SKILL_MODEL`, `INSIGHT_MODEL`, `INTERVIEW_MODEL`.

### Key flows
- **Resume path**: `POST /api/resume/upload` → PDF parsing → `extract_skills_from_text()` → `POST /api/skills/analyze` → `POST /api/roadmap/generate`
- **Manual path**: Role selector → same skills/roadmap endpoints
- **RAG**: ChromaDB `skill_resources` collection is seeded on startup in `services/rag.py:_seed_skills()`; queried before every LLM call via `retrieve_skill_context()`

### Frontend state
All cross-page state lives in `src/store/useAppStore.ts` (Zustand, persisted to localStorage). Pages redirect to `/` if `gapResult` is null.

### Roadmap JSON schema
The full schema is in `backend/services/roadmap_builder.py`. Key fields: `phases[].weeks[].resources[]`, `portfolio_projects`, `networking.discord_servers`, `networking.collab_platforms`, `export.opennote_markdown`.

## Environment

`backend/.env` (highest priority) overrides root `.env`. Required keys:
- `DATABASE_URL` — asyncpg connection string (Neon: strip `?sslmode=require`, handled automatically)
- `OLLAMA_MODEL` — default `nemotron-mini`, fallback `llama3.2:latest`
- `OPENROUTER_API_KEY` — free tier, fallback when Ollama is offline
- `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` — live job listings (has mock fallback)

## Fine-tuning & charts

| Script | Purpose |
|--------|---------|
| `backend/fine_tuning/generate_dataset.py` | Creates `data/finetune_dataset.jsonl` (Alpaca format) |
| `backend/fine_tuning/train_lora.py` | LoRA training via Unsloth (GPU required) |
| `backend/fine_tuning/compare_models.py` | Generates 4 comparison PNGs → `static/charts/` |

Charts are served at `GET /static/charts/*.png` and displayed at `/analytics`.
