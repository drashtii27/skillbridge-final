"""
SkillBridge AI — Clean Flowchart Diagram
Top-to-bottom flow, spacious, readable like a proper flowchart.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

FIG_W, FIG_H = 22, 34
DPI = 150
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("#080C1E")
ax.set_facecolor("#080C1E")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ── Palette ──────────────────────────────────────────────────────────────────
BG    = "#080C1E"
PANEL = "#0E1530"

NEON   = "#38BDF8"   # blue  — frontend / input
PURPLE = "#A78BFA"   # purple — backend / FastAPI
GREEN  = "#4ADE80"   # green  — ML / NER
AMBER  = "#FBBF24"   # amber  — database / RAG
TEAL   = "#2DD4BF"   # teal   — ChromaDB
PINK   = "#F472B6"   # pink   — jobs / export
RED    = "#F87171"   # red    — LLM
WHITE  = "#FFFFFF"
GRAY   = "#94A3B8"
DIM    = "#334155"


# ─────────────────────────────────────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def rbox(ax, cx, cy, w, h, color, line1, line2=None, line3=None,
         lsize=13, ssize=9.5, fill=None, lw=2.5):
    """Centered rounded rectangle."""
    fc = fill or PANEL
    x, y = cx - w/2, cy - h/2
    p = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.25",
        linewidth=lw, edgecolor=color, facecolor=fc, zorder=4)
    ax.add_patch(p)
    # glow
    g = FancyBboxPatch((x-0.08, y-0.08), w+0.16, h+0.16,
        boxstyle="round,pad=0,rounding_size=0.35",
        linewidth=0.8, edgecolor=color, facecolor="none", zorder=3, alpha=0.2)
    ax.add_patch(g)
    lines = [l for l in [line1, line2, line3] if l]
    offsets = {1: [0], 2: [0.22, -0.22], 3: [0.4, 0, -0.4]}[len(lines)]
    for txt, off in zip(lines, offsets):
        bold = (txt == line1)
        t = ax.text(cx, cy + off, txt, ha="center", va="center",
            fontsize=lsize if bold else ssize,
            fontweight="bold" if bold else "normal",
            color=WHITE if bold else GRAY, zorder=5)
        t.set_path_effects([pe.withStroke(linewidth=2, foreground=BG)])


def oval(ax, cx, cy, w, h, color, text, lsize=14):
    """Ellipse — start/end node."""
    from matplotlib.patches import Ellipse
    e = Ellipse((cx, cy), w, h, linewidth=2.5, edgecolor=color,
        facecolor=color + "33", zorder=4)
    ax.add_patch(e)
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=lsize, fontweight="bold", color=WHITE, zorder=5)


def diamond(ax, cx, cy, w, h, color, text, lsize=12):
    """Diamond — decision node."""
    dx, dy = w/2, h/2
    pts = [(cx, cy+dy), (cx+dx, cy), (cx, cy-dy), (cx-dx, cy)]
    poly = plt.Polygon(pts, closed=True, linewidth=2.5,
        edgecolor=color, facecolor=color + "33", zorder=4)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=lsize, fontweight="bold", color=WHITE, zorder=5)


def arw(ax, x1, y1, x2, y2, color=WHITE, lw=2.2, rad=0.0, size=16):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}", mutation_scale=size),
        zorder=6)


def line(ax, x1, y1, x2, y2, color=DIM, lw=1.8, dash=False):
    ls = "--" if dash else "-"
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, linestyle=ls,
        zorder=3, solid_capstyle="round")


def arw_label(ax, x, y, txt, color, fs=9):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs,
        color=color, zorder=7, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=BG,
                  edgecolor=color, linewidth=1.0, alpha=0.95))


def badge(ax, cx, cy, txt, color, w=2.0, h=0.38):
    p = FancyBboxPatch((cx-w/2, cy-h/2), w, h,
        boxstyle="round,pad=0,rounding_size=0.12",
        linewidth=0, facecolor=color+"44", zorder=5)
    ax.add_patch(p)
    ax.text(cx, cy, txt, ha="center", va="center",
        fontsize=8, fontweight="bold", color=color, zorder=6)


def swim_label(ax, txt, y_center, color, x=0.35):
    ax.text(x, y_center, txt, ha="center", va="center",
        fontsize=8.5, fontweight="bold", color=color, rotation=90,
        alpha=0.55, zorder=2)


# ─────────────────────────────────────────────────────────────────────────────
#  TITLE
# ─────────────────────────────────────────────────────────────────────────────
ax.text(FIG_W/2, 33.3, "SkillBridge AI — System Flowchart",
    ha="center", fontsize=22, fontweight="bold", color=WHITE, zorder=10)
ax.text(FIG_W/2, 32.75, "DATA 298B  ·  Team 04  ·  Spring 2026",
    ha="center", fontsize=11, color=GRAY, zorder=10)
ax.plot([1.0, FIG_W-1.0], [32.45, 32.45], color=NEON, lw=1.2, alpha=0.35)

CX = FIG_W / 2   # center x of main spine

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 1 — START
# ─────────────────────────────────────────────────────────────────────────────
oval(ax, CX, 31.5, 5.0, 0.9, NEON, "USER  (Browser / Web App)", lsize=13)

arw(ax, CX, 31.05, CX, 30.42, color=NEON)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 2 — INPUT DECISION
# ─────────────────────────────────────────────────────────────────────────────
diamond(ax, CX, 29.9, 5.2, 1.0, NEON, "How to start?", lsize=12)

# Left branch — Resume PDF
arw_label(ax, CX - 2.8, 29.9, "Resume PDF", NEON, fs=9)
arw(ax, CX - 2.6, 29.9, CX - 5.2, 29.9, color=NEON, lw=1.8, size=13)
line(ax, CX - 5.2, 29.9, CX - 5.2, 28.55, color=NEON, lw=1.8)

# Right branch — Manual role
arw_label(ax, CX + 2.8, 29.9, "Select Role", AMBER, fs=9)
arw(ax, CX + 2.6, 29.9, CX + 5.2, 29.9, color=AMBER, lw=1.8, size=13)
line(ax, CX + 5.2, 29.9, CX + 5.2, 28.55, color=AMBER, lw=1.8)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 3a — PDF PARSER (left branch)
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX - 5.2, 28.0, 5.8, 1.0, NEON,
     "PDF Parser", "pdfplumber + OCR fallback", "Digital & scanned PDFs",
     lsize=12, ssize=9)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 3b — MANUAL ROLE (right branch)
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX + 5.2, 28.0, 5.8, 1.0, AMBER,
     "Role Selector", "35 career roles available", "Sets target benchmark",
     lsize=12, ssize=9)

# Both branches merge down
line(ax, CX - 5.2, 27.5, CX - 5.2, 27.1, color=NEON, lw=1.8)
line(ax, CX + 5.2, 27.5, CX + 5.2, 27.1, color=AMBER, lw=1.8)
line(ax, CX - 5.2, 27.1, CX + 5.2, 27.1, color=GREEN, lw=1.8)
arw(ax, CX, 27.1, CX, 26.7, color=GREEN, size=14)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 4 — SKILL EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX, 25.95, 9.5, 1.35, GREEN,
     "Skill Extraction Engine",
     "GLiNER v0.5 (local NER, 10 entity types)  +  Mistral Small 24B (2nd-pass LLM)",
     "Regex fallback  →  Fuzzy-match normalization  →  Deduplicated skill list",
     lsize=13, ssize=9.5)

badge(ax, CX - 3.2, 26.82, "GLiNER  local · 0 API cost", GREEN)
badge(ax, CX + 3.0, 26.82, "Mistral 24B · OpenRouter", GREEN)

arw(ax, CX, 25.27, CX, 24.67, color=GREEN, size=15)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 5 — GAP ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX, 24.0, 9.5, 1.18, AMBER,
     "Skill Gap Analyzer",
     "User skills vs. 35 role benchmark profiles  →  missing_skills list",
     "Outputs: user_skills [ ]  ·  missing_skills [ ]  ·  match %",
     lsize=13, ssize=9.5)

arw(ax, CX, 23.41, CX, 22.82, color=TEAL, size=15)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 6 — CHROMADB RAG
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX, 22.15, 9.5, 1.22, TEAL,
     "ChromaDB RAG  (Vector Retrieval)",
     "Skill query  →  cosine similarity search  →  Top-3 course/resource matches",
     "Context injected into system prompt before every LLM call",
     lsize=13, ssize=9.5)

badge(ax, CX - 3.2, 21.62, "skill_resources  200+ embeddings", TEAL)
badge(ax, CX + 3.2, 21.62, "sentence-transformers MiniLM", TEAL)

arw(ax, CX, 21.54, CX, 20.9, color=RED, size=15)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 7 — NEMOTRON ROADMAP GENERATION  ★ MAIN MODEL ★
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX, 20.1, 11.0, 1.6, RED,
     "NVIDIA Nemotron Ultra 253B  (Roadmap Generator)",
     "Input: role + missing_skills + RAG context",
     "Output: 12-week roadmap  →  Week / Resources / Project / Checkpoint schema",
     lsize=14, ssize=10, fill="#170A18", lw=3.0)

badge(ax, CX - 4.0, 19.38, "LoRA fine-tuned  r=16", RED)
badge(ax, CX,       19.38, "nvidia/llama-3.1-nemotron-ultra-253b-v1:free", RED, w=5.8)
badge(ax, CX + 4.0, 19.38, "253B parameters", RED)

arw(ax, CX, 19.3, CX, 18.72, color=PURPLE, size=15)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 8 — FASTAPI STORES TO POSTGRES
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX, 18.06, 9.5, 1.18, PURPLE,
     "FastAPI Backend  (Persist + Route)",
     "Roadmap JSON  →  PostgreSQL  roadmaps table  (SQLAlchemy async)",
     "JWT auth  ·  XP awarded  ·  Badges checked  ·  Progress initialized",
     lsize=13, ssize=9.5)

# ─────────────────────────────────────────────────────────────────────────────
#  4-WAY BRANCH  ─ fan out to 4 parallel features
# ─────────────────────────────────────────────────────────────────────────────
branch_y_start = 17.47
branch_y_boxes = 15.5   # center y of the 4 feature boxes

BRANCH_XS = [2.5, 7.3, 14.7, 19.5]
BRANCH_COLORS = [AMBER, TEAL, GREEN, PINK]

# Spine down then horizontal line
line(ax, CX, branch_y_start, CX, 16.55, color=PURPLE, lw=2.0)
line(ax, BRANCH_XS[0], 16.55, BRANCH_XS[-1], 16.55, color=DIM, lw=1.8)

for bx, bc in zip(BRANCH_XS, BRANCH_COLORS):
    arw(ax, bx, 16.55, bx, 16.2, color=bc, lw=2.0, size=13)

# ─────────────────────────────────────────────────────────────────────────────
#  FEATURE BOXES (4 parallel)
# ─────────────────────────────────────────────────────────────────────────────
bw, bh = 4.0, 4.8

# Branch 1 — Dashboard & Roadmap
rbox(ax, BRANCH_XS[0], branch_y_boxes, bw, bh, AMBER,
     "Roadmap\nDashboard",
     "Timeline view\nPhase progress",
     None,
     lsize=12, ssize=9)
items_1 = [
    ("12-week phases", AMBER),
    ("Step completion", AMBER),
    ("XP + Badges", AMBER),
    ("OpenNote export", AMBER),
    ("JSON download", AMBER),
]
for i, (t, c) in enumerate(items_1):
    ax.text(BRANCH_XS[0], branch_y_boxes + 0.95 - i*0.58, f"• {t}",
        ha="center", fontsize=8.5, color=GRAY, zorder=5)

# Branch 2 — Job Search
rbox(ax, BRANCH_XS[1], branch_y_boxes, bw, bh, TEAL,
     "Job Market\nIntelligence",
     "DeepSeek R1 671B\n+ 4 Live Job APIs",
     None,
     lsize=12, ssize=9)
items_2 = [
    ("Remotive (no auth)", TEAL),
    ("Jobicy (no auth)", TEAL),
    ("The Muse (no auth)", TEAL),
    ("Adzuna (API key)", TEAL),
    ("asyncio.gather  <2s", TEAL),
]
for i, (t, c) in enumerate(items_2):
    ax.text(BRANCH_XS[1], branch_y_boxes + 0.95 - i*0.58, f"• {t}",
        ha="center", fontsize=8.5, color=GRAY, zorder=5)

# Branch 3 — Quiz
rbox(ax, BRANCH_XS[2], branch_y_boxes, bw, bh, GREEN,
     "Interview Quiz\n(15 MCQs)",
     "Qwen3 235B\nqwen/qwen3-235b-a22b:free",
     None,
     lsize=12, ssize=9)
items_3 = [
    ("15 questions", GREEN),
    ("30 sec / question", GREEN),
    ("80% pass threshold", GREEN),
    ("Per-skill breakdown", GREEN),
    ("Resource links", GREEN),
]
for i, (t, c) in enumerate(items_3):
    ax.text(BRANCH_XS[2], branch_y_boxes + 0.95 - i*0.58, f"• {t}",
        ha="center", fontsize=8.5, color=GRAY, zorder=5)

# Branch 4 — Interview Prep
rbox(ax, BRANCH_XS[3], branch_y_boxes, bw, bh, PINK,
     "Interview\nPrep",
     "Qwen3 235B\nFlashcard Q&A",
     None,
     lsize=12, ssize=9)
items_4 = [
    ("Role-specific Qs", PINK),
    ("Easy / Medium / Hard", PINK),
    ("Flip animation", PINK),
    ("Answer outlines", PINK),
    ("XP per session", PINK),
]
for i, (t, c) in enumerate(items_4):
    ax.text(BRANCH_XS[3], branch_y_boxes + 0.95 - i*0.58, f"• {t}",
        ha="center", fontsize=8.5, color=GRAY, zorder=5)

# ─────────────────────────────────────────────────────────────────────────────
#  MERGE — all 4 branches converge back
# ─────────────────────────────────────────────────────────────────────────────
merge_y = 12.7
for bx, bc in zip(BRANCH_XS, BRANCH_COLORS):
    line(ax, bx, branch_y_boxes - bh/2, bx, merge_y + 0.02, color=bc, lw=1.6)

line(ax, BRANCH_XS[0], merge_y, BRANCH_XS[-1], merge_y, color=DIM, lw=1.8)
arw(ax, CX, merge_y, CX, 12.28, color=PURPLE, size=15)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 9 — USER DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
rbox(ax, CX, 11.62, 9.5, 1.2, PURPLE,
     "User Dashboard  (Next.js 15)",
     "Roadmap timeline  ·  Job listings  ·  Quiz results  ·  Interview cards",
     "XP level bar  ·  Badge showcase  ·  Progress tracking per step",
     lsize=13, ssize=9.5)

arw(ax, CX, 11.02, CX, 10.42, color=PURPLE, size=15)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 10 — EXPORT / ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
# Split into 2 side by side
line(ax, CX, 10.42, CX, 10.1, color=PURPLE, lw=1.8)
line(ax, CX - 3.0, 10.1, CX + 3.0, 10.1, color=DIM, lw=1.8)
arw(ax, CX - 3.0, 10.1, CX - 3.0, 9.75, color=NEON, lw=1.8, size=12)
arw(ax, CX + 3.0, 10.1, CX + 3.0, 9.75, color=PINK, lw=1.8, size=12)

rbox(ax, CX - 3.0, 9.2, 5.5, 1.08, NEON,
     "Export Options",
     "OpenNote markdown  ·  JSON download",
     "/api/roadmap/{id}/export",
     lsize=11, ssize=9)

rbox(ax, CX + 3.0, 9.2, 5.5, 1.08, PINK,
     "Analytics Dashboard",
     "6 charts  ·  Model comparison  ·  /analytics",
     "ROUGE · BERTScore · FactScore · 4-model scale",
     lsize=11, ssize=9)

# ─────────────────────────────────────────────────────────────────────────────
#  NODE 11 — END
# ─────────────────────────────────────────────────────────────────────────────
line(ax, CX - 3.0, 8.66, CX - 3.0, 8.2, color=NEON, lw=1.6)
line(ax, CX + 3.0, 8.66, CX + 3.0, 8.2, color=PINK, lw=1.6)
line(ax, CX - 3.0, 8.2, CX + 3.0, 8.2, color=DIM, lw=1.8)
arw(ax, CX, 8.2, CX, 7.85, color=GREEN, size=14)

oval(ax, CX, 7.4, 6.0, 0.82, GREEN, "User achieves career goal", lsize=12)

# ─────────────────────────────────────────────────────────────────────────────
#  INFRASTRUCTURE SIDEBAR  (right side)
# ─────────────────────────────────────────────────────────────────────────────
SB_X = 19.8
SB_W = 4.0

ax.text(SB_X + SB_W/2, 6.85, "INFRASTRUCTURE",
    ha="center", fontsize=10, fontweight="bold", color=GRAY, zorder=6)
ax.plot([SB_X, SB_X + SB_W], [6.62, 6.62], color=DIM, lw=0.8)

infra = [
    ("PostgreSQL (Neon Cloud)", "8 tables · asyncpg · Alembic", AMBER),
    ("ChromaDB (Vector Store)", "3 collections · 200+ embeds", TEAL),
    ("JWT Auth + bcrypt", "Refresh tokens · Sessions", PURPLE),
    ("PostHog Analytics", "Event tracking · UX metrics", PINK),
    ("Docker Deployment", "backend + frontend + postgres", GREEN),
    ("OpenRouter (Free)", "4 LLMs · fallback chain", RED),
    ("Ollama Local Fallback", "nemotron-mini · llama3.2", NEON),
]
iy = 6.35
for title, detail, clr in infra:
    p = FancyBboxPatch((SB_X, iy - 0.52), SB_W, 0.72,
        boxstyle="round,pad=0,rounding_size=0.12",
        linewidth=1.2, edgecolor=clr, facecolor=PANEL, zorder=4)
    ax.add_patch(p)
    ax.text(SB_X + 0.18, iy - 0.16, title, ha="left", va="center",
        fontsize=8.5, fontweight="bold", color=clr, zorder=5)
    ax.text(SB_X + 0.18, iy - 0.44, detail, ha="left", va="center",
        fontsize=7.5, color=GRAY, zorder=5)
    iy -= 0.82

# ─────────────────────────────────────────────────────────────────────────────
#  EVALUATION SIDEBAR  (left side)
# ─────────────────────────────────────────────────────────────────────────────
EV_X = 0.3
EV_W = 4.0

ax.text(EV_X + EV_W/2, 6.85, "ML EVALUATION",
    ha="center", fontsize=10, fontweight="bold", color=GRAY, zorder=6)
ax.plot([EV_X, EV_X + EV_W], [6.62, 6.62], color=DIM, lw=0.8)

evals = [
    ("ROUGE-1 / ROUGE-L", "0.412  /  0.368 (fine-tuned)", NEON),
    ("Structure Score", "+242%   0.24 → 0.82", GREEN),
    ("Resource Richness", "+288%   0.13 → 0.50", GREEN),
    ("BERTScore F1", "0.873  (semantic quality)", TEAL),
    ("FactScore", "0.726  (hallucination check)", AMBER),
    ("Answer Relevance", "0.882  (on-topic accuracy)", PURPLE),
    ("Context Precision/Recall", "0.86 / 0.81  (RAG quality)", PINK),
    ("LoRA Training Loss", "2.8 → 0.4  (500 steps)", RED),
    ("4-Model Scale Test", "Nano→Super→Ultra monotonic +", NEON),
]
ey = 6.35
for title, val, clr in evals:
    p = FancyBboxPatch((EV_X, ey - 0.52), EV_W, 0.72,
        boxstyle="round,pad=0,rounding_size=0.12",
        linewidth=1.2, edgecolor=clr, facecolor=PANEL, zorder=4)
    ax.add_patch(p)
    ax.text(EV_X + 0.18, ey - 0.16, title, ha="left", va="center",
        fontsize=8.5, fontweight="bold", color=clr, zorder=5)
    ax.text(EV_X + 0.18, ey - 0.44, val, ha="left", va="center",
        fontsize=7.5, color=GRAY, zorder=5)
    ey -= 0.82

# ─────────────────────────────────────────────────────────────────────────────
#  STEP NUMBERS alongside main spine
# ─────────────────────────────────────────────────────────────────────────────
steps = [
    (31.5, "01", NEON),
    (29.9, "02", NEON),
    (25.95, "03", GREEN),
    (24.0, "04", AMBER),
    (22.15, "05", TEAL),
    (20.1, "06", RED),
    (18.06, "07", PURPLE),
    (11.62, "08", PURPLE),
]
for sy, num, clr in steps:
    circ = plt.Circle((5.0, sy), 0.32, color=clr, zorder=6)
    ax.add_patch(circ)
    ax.text(5.0, sy, num, ha="center", va="center",
        fontsize=9, fontweight="bold", color=BG, zorder=7)

# Step label for branch
circ2 = plt.Circle((5.0, branch_y_boxes), 0.32, color=PURPLE, zorder=6)
ax.add_patch(circ2)
ax.text(5.0, branch_y_boxes, "07b", ha="center", va="center",
    fontsize=8, fontweight="bold", color=BG, zorder=7)

# ─────────────────────────────────────────────────────────────────────────────
#  BOTTOM LEGEND
# ─────────────────────────────────────────────────────────────────────────────
legend_items = [
    ("User / Frontend", NEON),
    ("Skill Extraction ML", GREEN),
    ("Database / RAG", AMBER),
    ("ChromaDB", TEAL),
    ("LLM Models", RED),
    ("FastAPI Backend", PURPLE),
    ("Output / Export", PINK),
]
lx = 1.5
ly = 1.3
ax.text(lx, ly + 0.5, "COLOR LEGEND", ha="left", fontsize=9,
    fontweight="bold", color=GRAY)
for i, (lbl, clr) in enumerate(legend_items):
    circ = plt.Circle((lx + 0.2, ly - i*0.55), 0.14, color=clr, zorder=5)
    ax.add_patch(circ)
    ax.text(lx + 0.5, ly - i*0.55, lbl, ha="left", va="center",
        fontsize=9, color=GRAY, zorder=5)

# Key stats right side of bottom
stats = [
    ("5 Models", "Nemotron 253B · Mistral 24B · DeepSeek R1 · Qwen3 235B · GLiNER", NEON),
    ("8 DB Tables", "users · roadmaps · progress · quiz · jobs · sessions · eval", AMBER),
    ("9 Metrics", "ROUGE-1/L · Structure · Richness · BERTScore · FactScore · AR · CP · CR", GREEN),
    ("4 Job Sources", "Remotive · Jobicy · The Muse · Adzuna", TEAL),
]
sx = 9.5
for i, (title, detail, clr) in enumerate(stats):
    bx_ = sx + i * 3.2
    p = FancyBboxPatch((bx_, 0.18), 3.0, 1.2,
        boxstyle="round,pad=0,rounding_size=0.18",
        linewidth=1.5, edgecolor=clr, facecolor=PANEL, zorder=4)
    ax.add_patch(p)
    ax.text(bx_ + 1.5, 0.98, title, ha="center", va="center",
        fontsize=10.5, fontweight="bold", color=clr, zorder=5)
    for j, part in enumerate(detail.split(" · ")):
        ax.text(bx_ + 1.5, 0.65 - j*0.25, "· " + part,
            ha="center", va="center", fontsize=7, color=GRAY, zorder=5)

# ─────────────────────────────────────────────────────────────────────────────
#  SAVE
# ─────────────────────────────────────────────────────────────────────────────
out = "/Users/drashtibhingradiya/Desktop/SkillBridge_System_Architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved -> {out}   ({int(FIG_W*DPI)} x {int(FIG_H*DPI)} px)")
