"""
SkillBridge AI — Full System Architecture Diagram
Generates a massive high-resolution PNG flowchart on the Desktop.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ─── Canvas ───────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 32, 22   # inches — poster-size
DPI = 150                # 4800 × 3300 px

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("#07091A")
ax.set_facecolor("#07091A")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ─── Color palette ────────────────────────────────────────────────────────────
C = {
    "bg":       "#07091A",
    "panel":    "#0D1529",
    "panel2":   "#0F1B36",
    "border":   "#1E3A5F",
    "neon":     "#38BDF8",   # sky blue
    "purple":   "#A78BFA",
    "green":    "#4ADE80",
    "amber":    "#FBBF24",
    "teal":     "#2DD4BF",
    "red":      "#F87171",
    "pink":     "#F472B6",
    "white":    "#FFFFFF",
    "gray":     "#94A3B8",
    "dimgray":  "#475569",
    "row1":     "#0E1627",
    "row2":     "#121E35",
}

# ─── Drawing helpers ──────────────────────────────────────────────────────────

def box(ax, x, y, w, h, color, label, sublabel=None,
        fontsize=11, subsize=8.5, radius=0.25, alpha=0.95,
        label_color="#FFFFFF", sub_color="#94A3B8",
        icon=None, border_width=2.0, fill_color=None):
    fc = fill_color or C["panel2"]
    rect = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        linewidth=border_width, edgecolor=color,
        facecolor=fc, zorder=3, alpha=alpha)
    ax.add_patch(rect)
    # Glow effect on border
    rect2 = FancyBboxPatch((x-0.05, y-0.05), w+0.1, h+0.1,
        boxstyle=f"round,pad=0.0,rounding_size={radius+0.1}",
        linewidth=1.0, edgecolor=color, facecolor="none",
        zorder=2, alpha=0.18)
    ax.add_patch(rect2)

    lbl_y = y + h/2 + (0.18 if sublabel else 0)
    txt = ax.text(x + w/2, lbl_y, (icon + "  " if icon else "") + label,
        ha="center", va="center", fontsize=fontsize, fontweight="bold",
        color=label_color, zorder=5)
    txt.set_path_effects([pe.withStroke(linewidth=3, foreground=C["bg"])])

    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.22, sublabel,
            ha="center", va="center", fontsize=subsize,
            color=sub_color, zorder=5, style="italic",
            wrap=True)


def header_box(ax, x, y, w, h, color, label, icon=""):
    """Larger header / section box."""
    rect = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.0,rounding_size=0.3",
        linewidth=2.5, edgecolor=color,
        facecolor=color + "22",   # 13% opacity tint
        zorder=3)
    ax.add_patch(rect)
    # Top solid accent bar
    bar = FancyBboxPatch((x, y + h - 0.42), w, 0.42,
        boxstyle="round,pad=0,rounding_size=0.15",
        linewidth=0, edgecolor="none", facecolor=color + "55",
        zorder=4)
    ax.add_patch(bar)
    ax.text(x + w/2, y + h - 0.21, icon + "  " + label,
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=color, zorder=5)


def arrow(ax, x1, y1, x2, y2, color="#38BDF8", lw=1.8,
          style="->", arrowsize=14, alpha=0.85, rad=0.0):
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle=f"-|>",
            color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}",
            mutation_scale=arrowsize,
        ),
        zorder=6, alpha=alpha)


def dashed_arrow(ax, x1, y1, x2, y2, color="#475569", lw=1.2):
    ax.annotate("",
        xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(
            arrowstyle="-|>",
            color=color, lw=lw,
            linestyle="dashed",
            connectionstyle="arc3,rad=0",
            mutation_scale=10,
        ),
        zorder=6, alpha=0.6)


def label_arrow(ax, x, y, text, color, fontsize=8):
    ax.text(x, y, text, ha="center", va="center",
        fontsize=fontsize, color=color, zorder=7,
        bbox=dict(boxstyle="round,pad=0.2", facecolor=C["bg"],
                  edgecolor=color, linewidth=0.8, alpha=0.9))


def section_bg(ax, x, y, w, h, color, label, alpha=0.06):
    rect = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.4",
        linewidth=1.2, edgecolor=color,
        facecolor=color, zorder=1, alpha=alpha)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.25, label,
        ha="left", va="top", fontsize=9, fontweight="bold",
        color=color, alpha=0.55, zorder=2)


def dot(ax, x, y, color, r=0.12):
    circle = plt.Circle((x, y), r, color=color, zorder=7)
    ax.add_patch(circle)


def mini_table(ax, x, y, w, rows, color, fontsize=7.8):
    row_h = 0.32
    for i, (k, v) in enumerate(rows):
        ry = y - i * row_h
        bg = C["row1"] if i % 2 == 0 else C["row2"]
        rect = mpatches.Rectangle((x, ry - row_h + 0.04), w, row_h - 0.04,
            facecolor=bg, edgecolor="none", zorder=4)
        ax.add_patch(rect)
        ax.text(x + 0.12, ry - row_h/2 + 0.04, k,
            ha="left", va="center", fontsize=fontsize, color=color, zorder=5, fontweight="bold")
        ax.text(x + w - 0.12, ry - row_h/2 + 0.04, v,
            ha="right", va="center", fontsize=fontsize, color=C["gray"], zorder=5)


# ══════════════════════════════════════════════════════════════════════════════
#  TITLE
# ══════════════════════════════════════════════════════════════════════════════

ax.text(FIG_W/2, 21.45, "SkillBridge AI — Full System Architecture",
    ha="center", va="center", fontsize=26, fontweight="bold",
    color=C["white"], zorder=10)
ax.text(FIG_W/2, 21.0, "DATA 298B · Team 04 · Spring 2026  |  "
    "Next.js 15  ·  FastAPI  ·  PostgreSQL  ·  ChromaDB  ·  OpenRouter  ·  GLiNER  ·  Docker",
    ha="center", va="center", fontsize=11, color=C["gray"], zorder=10)

# Title underline
ax.plot([1, FIG_W-1], [20.72, 20.72], color=C["neon"], lw=1.5, alpha=0.4, zorder=5)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 1 — USER / BROWSER
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 0.5, 19.1, 31, 1.45, C["dimgray"], "LAYER 0 — USER / CLIENT", alpha=0.08)

user_items = [
    ("Resume PDF Upload",  C["neon"]),
    ("Role Selection",     C["teal"]),
    ("Dashboard View",     C["purple"]),
    ("Quiz / Interview",   C["green"]),
    ("Job Search",         C["amber"]),
    ("Analytics",          C["pink"]),
    ("Export Roadmap",     C["teal"]),
]

box_w, box_h = 3.8, 0.85
start_x = 1.0
gap = (31 - start_x - len(user_items) * box_w) / (len(user_items) - 1)
for i, (label, color) in enumerate(user_items):
    bx = start_x + i * (box_w + gap)
    box(ax, bx, 19.25, box_w, box_h, color, label,
        fontsize=9.5, radius=0.2, border_width=1.5)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 2 — NEXT.JS FRONTEND
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 0.5, 15.7, 31, 3.2, C["neon"], "LAYER 1 — NEXT.JS 15 FRONTEND  (Port 3000)", alpha=0.05)

# Browser arrows down to frontend
for i, (_, color) in enumerate(user_items):
    bx = start_x + i * (box_w + gap) + box_w / 2
    arrow(ax, bx, 19.25, bx, 18.88, color=color, lw=1.2, arrowsize=10, alpha=0.5)

# Frontend pages
pages = [
    ("/  Home + Hero",         "CinematicHeroBg\nFramer Motion",       C["neon"]),
    ("/dashboard\nSkills & Gaps", "Skill cards\nGap analysis",          C["purple"]),
    ("/dashboard\nRoadmap",    "Phase timeline\nProgress tracker",      C["amber"]),
    ("/dashboard\nInterview",  "Flashcards\n15Q Quiz / 80% threshold",  C["green"]),
    ("/dashboard\nJobs",       "4-source live\njob listings",           C["teal"]),
    ("/analytics",             "6 charts\nModel comparison",            C["pink"]),
    ("/api/* proxy\n→ FastAPI", "All /api/* &\n/static/* forwarded",   C["dimgray"]),
]

pg_w = 3.85
pg_gap = (31 - 1.0 - len(pages) * pg_w) / (len(pages) - 1)
for i, (label, sub, color) in enumerate(pages):
    px = 1.0 + i * (pg_w + pg_gap)
    box(ax, px, 16.5, pg_w, 2.1, color, label, sub,
        fontsize=9, subsize=8, radius=0.22, border_width=1.8)

# State + analytics bar
box(ax, 1.0, 15.88, 9.5, 0.5, C["purple"],
    "Zustand Store  (localStorage persist)  —  cross-page state: gapResult · roadmap · skills · user",
    fontsize=8.5, radius=0.18, border_width=1.2)
box(ax, 11.2, 15.88, 9.5, 0.5, C["pink"],
    "PostHog Analytics  —  event tracking: resume_uploaded · roadmap_generated · quiz_submitted · job_clicked",
    fontsize=8.5, radius=0.18, border_width=1.2)
box(ax, 21.4, 15.88, 10.1, 0.5, C["neon"],
    "Next.js Rewrites  —  /api/:path* → http://backend:8000/api/:path*  ·  /static/:path* → backend",
    fontsize=8.5, radius=0.18, border_width=1.2)

# ══════════════════════════════════════════════════════════════════════════════
#  ARROW FRONTEND → BACKEND
# ══════════════════════════════════════════════════════════════════════════════

ax.plot([FIG_W/2, FIG_W/2], [15.7, 14.95], color=C["neon"], lw=2.5, zorder=6)
arrow(ax, FIG_W/2, 14.95, FIG_W/2, 14.82, color=C["neon"], lw=2.5, arrowsize=16)
label_arrow(ax, FIG_W/2 + 1.8, 15.32, "HTTPS / JSON", C["neon"], fontsize=9)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 3 — FASTAPI BACKEND
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 0.5, 11.35, 31, 3.3, C["purple"], "LAYER 2 — FASTAPI BACKEND  (Port 8000)", alpha=0.05)

# API route boxes
routes = [
    ("POST /api/resume\n/upload",  "PDF → OCR → NER\n→ skill extraction",  C["neon"]),
    ("POST /api/skills\n/analyze", "Gap analysis\n35 role benchmarks",      C["teal"]),
    ("POST /api/roadmap\n/generate","Nemotron 253B\nLoRA schema",           C["purple"]),
    ("GET  /api/jobs\n/search",    "4-source scraper\nasyncio.gather()",    C["amber"]),
    ("GET  /api/quiz\n/questions", "Qwen3 235B\n15 MCQ generation",        C["green"]),
    ("GET  /api/interview\n/questions","Qwen3 235B\nflashcard Q&A",        C["green"]),
    ("POST /api/auth\n/login|register","JWT + bcrypt\nNeon PostgreSQL",    C["pink"]),
    ("GET  /api/insight\n/market", "DeepSeek R1\nRAG + trends",            C["teal"]),
]

rt_w = 3.55
rt_gap = (31 - 1.0 - len(routes) * rt_w) / (len(routes) - 1)
for i, (label, sub, color) in enumerate(routes):
    rx = 1.0 + i * (rt_w + rt_gap)
    box(ax, rx, 13.55, rt_w, 1.6, color, label, sub,
        fontsize=8.5, subsize=7.8, radius=0.2, border_width=1.8)

# Middleware bar
box(ax, 1.0, 12.5, 14.5, 0.88,  C["purple"],
    "Middleware Stack",
    "Auth: JWT decode + get_current_user()  ·  CORS: allow all origins  ·  Rate limiting  ·  SQLAlchemy async session injection",
    fontsize=10, subsize=8, radius=0.2)
box(ax, 16.2, 12.5, 15.3, 0.88, C["dimgray"],
    "Services Layer",
    "llm.py (4 model routers)  ·  rag.py (ChromaDB)  ·  jobs_fetcher.py  ·  pdf_parser.py  ·  skill_analyzer.py  ·  roadmap_builder.py",
    fontsize=10, subsize=8, radius=0.2)

# Bottom bar — dep injection
box(ax, 1.0, 11.55, 31, 0.72, C["border"],
    "FastAPI Dependency Injection",
    "get_db() → AsyncSession  ·  get_current_user() → User | None  ·  get_optional_user()  ·  get_settings() → pydantic Settings",
    fontsize=9.5, subsize=8, radius=0.18, border_width=1.2)

# ══════════════════════════════════════════════════════════════════════════════
#  ARROWS BACKEND → DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════

# 4 diverging arrows to the 4 data stores
data_xs = [3.5, 10.5, 19.5, 27.5]
data_colors = [C["teal"], C["amber"], C["neon"], C["green"]]
for dx, dc in zip(data_xs, data_colors):
    ax.plot([FIG_W/2, dx], [11.35, 10.1], color=dc, lw=1.8,
            linestyle="--", alpha=0.5, zorder=4)
    arrow(ax, dx, 10.1, dx, 9.88, color=dc, lw=1.8, arrowsize=13)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 4A — DATABASES (left half)
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 0.5, 5.2, 14.5, 4.7, C["teal"], "LAYER 3A — DATA STORES", alpha=0.05)

# PostgreSQL
header_box(ax, 0.7, 7.8, 6.8, 2.0, C["teal"], "PostgreSQL (Neon Cloud)", icon="[DB]")
pg_tables = [
    ("users",               "email · hashed_pw · xp · badges · avatar"),
    ("sessions",            "refresh_token · expires_at · user_id FK"),
    ("roadmaps",            "role · skills JSON · roadmap_json · model_used"),
    ("user_progress",       "completed_steps · quiz_scores · roadmap_id FK"),
    ("interview_questions", "role · question · difficulty · answer_outline"),
    ("quiz_questions",      "question · options · correct_index · skill_tag"),
    ("jobs",                "source · title · company · salary · url · hash"),
    ("evaluation_runs",     "model_name · is_finetuned · metrics JSON"),
]
mini_table(ax, 0.7, 7.65, 6.8, pg_tables, C["teal"], fontsize=7.2)

# ChromaDB
header_box(ax, 7.8, 7.8, 6.8, 2.0, C["amber"], "ChromaDB (Vector Store)", icon="[VEC]")
chroma_tables = [
    ("skill_resources",      "200+ skill→course embeddings (seeded at startup)"),
    ("job_descriptions",     "Job skill requirements embeddings"),
    ("interview_questions",  "Interview Q&A embeddings for retrieval"),
    ("Embedding model",      "sentence-transformers/all-MiniLM-L6-v2"),
    ("Retrieval",            "Top-3 cosine similarity match per skill"),
    ("Injection point",      "Injected into system prompt before every LLM call"),
]
mini_table(ax, 7.8, 7.65, 6.8, chroma_tables, C["amber"], fontsize=7.2)

# Alembic + SQLAlchemy
box(ax, 0.7, 5.4, 6.8, 2.2, C["dimgray"],
    "SQLAlchemy Async ORM",
    "asyncpg driver  ·  AsyncSession  ·  Alembic migrations\n"
    "Models: User · Session · Roadmap · UserProgress\n"
    "InterviewQuestion · QuizQuestion · Job · EvaluationRun",
    fontsize=9, subsize=8, radius=0.2)

box(ax, 7.8, 5.4, 6.8, 2.2, C["dimgray"],
    "RAG Pipeline",
    "retrieve_skill_context(skill) → ChromaDB similarity search\n"
    "→ Top-3 results as context string\n"
    "→ Prepended to every LLM system prompt\n"
    "Reduces hallucination · grounds in real courses",
    fontsize=9, subsize=8, radius=0.2)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 4B — AI / ML MODELS (right half)
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 15.5, 5.2, 16, 4.7, C["neon"], "LAYER 3B — AI / ML MODELS", alpha=0.05)

# OpenRouter
header_box(ax, 15.7, 7.8, 15.6, 2.0, C["neon"], "OpenRouter API — 4 Specialized LLMs (Free Tier)", icon="[AI]")

llm_cols = [
    ("Model 1\nNemotron Ultra 253B", "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
     "Roadmap generation\nLoRA fine-tuned schema\nWeek/Resources/\nProject/Checkpoint\n12-week plans", C["neon"]),
    ("Model 2\nMistral Small 24B",   "mistralai/mistral-small-3.2-24b-instruct:free",
     "Skill extraction\n2nd-pass NER\nDomain-specific\nskills missed\nby GLiNER", C["purple"]),
    ("Model 3\nDeepSeek R1 671B MoE","deepseek/deepseek-r1:free",
     "Market insight\nRAG + reasoning\nChain-of-thought\n~22B active\nparams per token", C["teal"]),
    ("Model 4\nQwen3 235B",          "qwen/qwen3-235b-a22b:free",
     "Interview Qs\n15-MCQ quiz gen\n4-option format\nskill tags &\nexplanations", C["amber"]),
]

col_w = 3.6
for i, (name, model_id, desc, clr) in enumerate(llm_cols):
    cx = 15.85 + i * (col_w + 0.3)
    box(ax, cx, 5.42, col_w, 4.18, clr, name,
        fontsize=9, radius=0.22, border_width=2.0, fill_color=C["panel"])
    # model id
    ax.text(cx + col_w/2, 8.95, model_id,
        ha="center", va="center", fontsize=6.5, color=clr,
        style="italic", zorder=6)
    # description lines
    for j, line in enumerate(desc.split("\n")):
        ax.text(cx + col_w/2, 8.6 - j * 0.42, line,
            ha="center", va="center", fontsize=7.8, color=C["gray"], zorder=6)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 4C — EXTRACTION / NER (bottom left)
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 0.5, 1.2, 14.5, 3.8, C["green"], "LAYER 3C — LOCAL ML + EXTERNAL APIs", alpha=0.05)

# GLiNER
header_box(ax, 0.7, 3.65, 6.8, 1.35, C["green"], "GLiNER v0.5  (Local NER Model)", icon="[NER]")
gliner_rows = [
    ("Type",           "Multi-label Span-based NER"),
    ("Entity types",   "10 engineering: lang · framework · tool · hw-skill · EE-component"),
    ("Execution",      "Local — pre-warmed at startup, zero API cost"),
    ("Speed",          "~120ms per resume on CPU"),
    ("Fallback",       "Regex pattern matching for common skill keywords"),
]
mini_table(ax, 0.7, 3.5, 6.8, gliner_rows, C["green"], fontsize=7.2)

box(ax, 0.7, 1.4, 6.8, 1.95, C["green"],
    "LoRA Fine-Tuning Pipeline",
    "generate_dataset.py → 300 Alpaca JSONL examples\n"
    "train_lora.py → Unsloth LoRA  r=16 · α=32 · dropout=0.05\n"
    "Target: q_proj · k_proj · v_proj · o_proj  (<1% of params)\n"
    "Training loss: 2.8 → 0.4 · 500 steps · ~45 min on GPU",
    fontsize=9, subsize=8, radius=0.2)

# Job scraper
header_box(ax, 7.8, 3.65, 6.8, 1.35, C["amber"], "Multi-Source Job Scraper", icon="[WEB]")
job_rows = [
    ("Remotive",    "remotive.com/api/remote-jobs  — no auth"),
    ("Jobicy",      "jobicy.com/api/v2/remote-jobs  — no auth"),
    ("The Muse",    "themuse.com/api/public/jobs  — no auth"),
    ("Adzuna",      "api.adzuna.com  — optional API key"),
    ("Concurrency", "asyncio.gather() — all 4 in parallel, <2s"),
    ("Dedup",       "MD5 hash(title+company) across sources"),
]
mini_table(ax, 7.8, 3.5, 6.8, job_rows, C["amber"], fontsize=7.2)

box(ax, 7.8, 1.4, 6.8, 1.95, C["amber"],
    "Model Evaluation Framework",
    "compare_models.py → 10 test cases · 9 metrics\n"
    "Classical: ROUGE-1 · ROUGE-L · Structure Score · Resource Richness\n"
    "Modern: BERTScore F1 · FactScore · Answer Relevance\n"
    "RAG: Context Precision · Context Recall\n"
    "6 charts → static/charts/ → visible at /analytics",
    fontsize=9, subsize=8, radius=0.2)

# ══════════════════════════════════════════════════════════════════════════════
#  LAYER 4D — DEPLOYMENT (bottom right)
# ══════════════════════════════════════════════════════════════════════════════

section_bg(ax, 15.5, 1.2, 16, 3.8, C["pink"], "LAYER 3D — DEPLOYMENT & INFRASTRUCTURE", alpha=0.05)

deploy_items = [
    ("[Docker]  Dockerfile.backend",
     "Python 3.11-slim\ninstalls requirements.txt\nuvicorn --workers 2\nHEALTHCHECK: /api/health",
     C["neon"]),
    ("[Docker]  Dockerfile.frontend",
     "Stage 1: node:20 npm ci + build\nnext.config.ts: output=standalone\nStage 2: minimal runner\nHEALTHCHECK: wget localhost:3000",
     C["purple"]),
    ("⚙️  docker-compose.yml",
     "postgres:16-alpine\nbackend (depends_on: postgres healthy)\nfrontend (depends_on: backend healthy)\ncharts_data volume",
     C["teal"]),
    ("[Cloud]  Cloud Deploy",
     "Push images → Docker Hub\nRailway · Render · AWS ECS\nGCP Cloud Run · Azure ACI\nLLMs via OpenRouter (no GPU)",
     C["green"]),
]

dep_w = 3.6
for i, (title, desc, clr) in enumerate(deploy_items):
    dx = 15.7 + i * (dep_w + 0.28)
    box(ax, dx, 1.4, dep_w, 3.55, clr, title, desc,
        fontsize=9, subsize=8, radius=0.22, border_width=1.8, fill_color=C["panel"])

# ══════════════════════════════════════════════════════════════════════════════
#  CROSS-CUTTING ARROWS
# ══════════════════════════════════════════════════════════════════════════════

# Backend → PostgreSQL
arrow(ax, 4.0, 11.55, 4.0, 9.8, color=C["teal"], lw=2.0, arrowsize=14)
label_arrow(ax, 5.2, 10.65, "SQLAlchemy\nasync ORM", C["teal"], fontsize=7.5)

# Backend → ChromaDB
arrow(ax, 11.2, 11.55, 11.2, 9.8, color=C["amber"], lw=2.0, arrowsize=14)
label_arrow(ax, 12.4, 10.65, "RAG\nretrieve()", C["amber"], fontsize=7.5)

# Backend → OpenRouter (LLMs)
arrow(ax, 21.5, 11.55, 21.5, 9.78, color=C["neon"], lw=2.0, arrowsize=14)
label_arrow(ax, 22.9, 10.65, "HTTP\nOpenRouter", C["neon"], fontsize=7.5)

# Backend → Job APIs
arrow(ax, 27.5, 11.55, 27.5, 5.6, color=C["amber"], lw=1.8, arrowsize=13, rad=0.0)
label_arrow(ax, 28.9, 8.5, "async\nHTTP", C["amber"], fontsize=7.5)

# Backend → GLiNER
arrow(ax, 3.0, 11.55, 3.0, 5.0, color=C["green"], lw=1.8, arrowsize=13, rad=0.0)
label_arrow(ax, 1.6, 8.3, "Local\nNER call", C["green"], fontsize=7.5)

# ChromaDB → LLMs (RAG context injected)
ax.annotate("",
    xy=(16.5, 7.65), xytext=(13.5, 7.5),
    arrowprops=dict(arrowstyle="-|>", color=C["amber"], lw=1.5,
                    linestyle="dashed", connectionstyle="arc3,rad=-0.3",
                    mutation_scale=12),
    zorder=6, alpha=0.7)
label_arrow(ax, 15.0, 8.05, "RAG context\ninjected to\nsystem prompt", C["amber"], fontsize=7)

# LoRA model affects Nemotron
ax.annotate("",
    xy=(16.0, 5.8), xytext=(7.0, 3.3),
    arrowprops=dict(arrowstyle="-|>", color=C["green"], lw=1.5,
                    linestyle="dashed", connectionstyle="arc3,rad=-0.25",
                    mutation_scale=11),
    zorder=6, alpha=0.6)
label_arrow(ax, 11.5, 4.8, "Fine-tuned\nadapter", C["green"], fontsize=7)

# ══════════════════════════════════════════════════════════════════════════════
#  USER FLOW CALLOUT (Data pipeline summary — top right)
# ══════════════════════════════════════════════════════════════════════════════

flow_x, flow_y = 22.0, 20.55
flow_steps = [
    ("① PDF Upload",      C["neon"]),
    ("② GLiNER + Mistral","skill extraction",   C["green"]),
    ("③ Gap Analysis",    "vs 35 roles",         C["teal"]),
    ("④ RAG fetch",       "ChromaDB top-3",      C["amber"]),
    ("⑤ Nemotron 253B",  "roadmap generation",  C["purple"]),
    ("⑥ Enrichment",     "jobs + quiz + insight",C["pink"]),
    ("⑦ Store + Export", "PostgreSQL + markdown",C["neon"]),
]
ax.text(flow_x, flow_y + 0.22, "USER DATA FLOW",
    ha="left", fontsize=9, fontweight="bold", color=C["white"], zorder=10)

for i, item in enumerate(flow_steps):
    fy = flow_y - 0.05 - i * 0.38
    if len(item) == 2:
        lbl, clr = item
        sub = ""
    else:
        lbl, sub, clr = item
    dot(ax, flow_x + 0.18, fy, clr, r=0.1)
    ax.text(flow_x + 0.42, fy, lbl,
        ha="left", va="center", fontsize=8.5, fontweight="bold",
        color=clr, zorder=10)
    if sub:
        ax.text(flow_x + 3.1, fy, sub,
            ha="left", va="center", fontsize=7.5, color=C["gray"], zorder=10)
    if i < len(flow_steps) - 1:
        ax.plot([flow_x + 0.18, flow_x + 0.18], [fy - 0.1, fy - 0.28],
            color=C["dimgray"], lw=1.0, zorder=9)

# ══════════════════════════════════════════════════════════════════════════════
#  LEGEND
# ══════════════════════════════════════════════════════════════════════════════

legend_x = 0.7
legend_y = 20.62
ax.text(legend_x, legend_y + 0.22, "LEGEND",
    ha="left", fontsize=9, fontweight="bold", color=C["white"], zorder=10)

legend_items = [
    (C["neon"],   "Next.js Frontend / Nemotron 253B"),
    (C["purple"], "FastAPI Backend / Mistral 24B"),
    (C["teal"],   "PostgreSQL / RAG / DeepSeek R1"),
    (C["amber"],  "ChromaDB / Job APIs / Qwen3 235B"),
    (C["green"],  "GLiNER NER / LoRA Fine-Tuning"),
    (C["pink"],   "PostHog Analytics / Docker Deploy"),
]
for i, (clr, label) in enumerate(legend_items):
    dot(ax, legend_x + 0.18, legend_y - i * 0.35, clr, r=0.09)
    ax.text(legend_x + 0.42, legend_y - i * 0.35, label,
        ha="left", va="center", fontsize=8, color=C["gray"], zorder=10)

# ══════════════════════════════════════════════════════════════════════════════
#  METRICS BOX (bottom strip)
# ══════════════════════════════════════════════════════════════════════════════

metrics = [
    ("5 Models",            "Nemotron 253B · Mistral 24B · DeepSeek R1 · Qwen3 235B · GLiNER", C["neon"]),
    ("8 DB Tables",         "users · sessions · roadmaps · progress · quiz · interview · jobs · eval", C["teal"]),
    ("9 Eval Metrics",      "ROUGE-1/L · Structure · Richness · BERTScore · FactScore · AR · CP · CR", C["amber"]),
    ("4 Job Sources",       "Remotive · Jobicy · The Muse · Adzuna  (asyncio.gather, <2s)", C["green"]),
    ("6 Chart PNGs",        "bar · radar · scatter · training_loss · modern_metrics · comparison", C["pink"]),
    ("Docker Ready",        "Dockerfile.backend + Dockerfile.frontend + docker-compose.yml", C["purple"]),
]

strip_w = (FIG_W - 1.0) / len(metrics)
for i, (title, desc, clr) in enumerate(metrics):
    sx = 0.5 + i * strip_w
    rect = FancyBboxPatch((sx + 0.05, 0.08), strip_w - 0.1, 0.95,
        boxstyle="round,pad=0,rounding_size=0.15",
        linewidth=1.2, edgecolor=clr,
        facecolor=C["panel"], zorder=3)
    ax.add_patch(rect)
    ax.text(sx + strip_w/2, 0.68, title,
        ha="center", va="center", fontsize=9, fontweight="bold",
        color=clr, zorder=5)
    ax.text(sx + strip_w/2, 0.32, desc,
        ha="center", va="center", fontsize=6.8, color=C["gray"], zorder=5)

# Bottom border line
ax.plot([0.5, FIG_W - 0.5], [1.15, 1.15], color=C["dimgray"], lw=0.8, alpha=0.5)

# ══════════════════════════════════════════════════════════════════════════════
#  SAVE
# ══════════════════════════════════════════════════════════════════════════════

out_path = "/Users/drashtibhingradiya/Desktop/SkillBridge_System_Architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out_path, dpi=DPI, bbox_inches="tight",
            facecolor=C["bg"], edgecolor="none")
plt.close()
print(f"✅ Architecture diagram saved → {out_path}")
print(f"   Size: {FIG_W*DPI:.0f} × {FIG_H*DPI:.0f} px  ({DPI} DPI)")
