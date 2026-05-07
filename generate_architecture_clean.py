"""
SkillBridge AI — Clean System Architecture Diagram
Clear, spacious, readable — designed for presentations.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

FIG_W, FIG_H = 28, 20
DPI = 160

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("#06091A")
ax.set_facecolor("#06091A")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ── Palette ──────────────────────────────────────────────────────────────────
BG       = "#06091A"
PANEL    = "#0D1630"
PANEL2   = "#111E3A"
NEON     = "#38BDF8"
PURPLE   = "#A78BFA"
GREEN    = "#4ADE80"
AMBER    = "#FBBF24"
TEAL     = "#2DD4BF"
PINK     = "#F472B6"
WHITE    = "#FFFFFF"
GRAY     = "#94A3B8"
DIMGRAY  = "#374151"
BORDER   = "#1E3A5F"

# ── Helpers ───────────────────────────────────────────────────────────────────

def rbox(ax, x, y, w, h, edge, label, sub=None,
         lsize=13, ssize=9.5, fill=PANEL, lcolor=WHITE, scolor=GRAY,
         lw=2.2, r=0.3):
    """Rounded rectangle with optional subtitle."""
    p = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=lw, edgecolor=edge, facecolor=fill, zorder=3)
    ax.add_patch(p)
    # subtle glow
    g = FancyBboxPatch((x-0.06, y-0.06), w+0.12, h+0.12,
        boxstyle=f"round,pad=0,rounding_size={r+0.1}",
        linewidth=0.8, edgecolor=edge, facecolor="none", zorder=2, alpha=0.2)
    ax.add_patch(g)
    ly = y + h/2 + (0.2 if sub else 0)
    t = ax.text(x+w/2, ly, label, ha="center", va="center",
        fontsize=lsize, fontweight="bold", color=lcolor, zorder=5)
    t.set_path_effects([pe.withStroke(linewidth=2.5, foreground=BG)])
    if sub:
        ax.text(x+w/2, y+h/2-0.25, sub, ha="center", va="center",
            fontsize=ssize, color=scolor, zorder=5)


def section(ax, x, y, w, h, edge, title, alpha=0.07):
    """Shaded zone with header label."""
    p = FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.4",
        linewidth=1.5, edgecolor=edge, facecolor=edge, zorder=1, alpha=alpha)
    ax.add_patch(p)
    # top accent strip
    strip = FancyBboxPatch((x, y+h-0.42), w, 0.42,
        boxstyle="round,pad=0,rounding_size=0.18",
        linewidth=0, edgecolor="none", facecolor=edge, zorder=2, alpha=0.28)
    ax.add_patch(strip)
    ax.text(x+0.3, y+h-0.21, title, ha="left", va="center",
        fontsize=11, fontweight="bold", color=edge, zorder=3, alpha=0.9)


def arw(ax, x1, y1, x2, y2, color=NEON, lw=2.0, rad=0.0, size=15):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
            connectionstyle=f"arc3,rad={rad}", mutation_scale=size),
        zorder=7)


def alabel(ax, x, y, txt, color, fs=8.5):
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs,
        color=color, zorder=8,
        bbox=dict(boxstyle="round,pad=0.25", facecolor=BG,
                  edgecolor=color, linewidth=0.9, alpha=0.92))


def hline(ax, y, color=BORDER, alpha=0.45, lw=1.0):
    ax.plot([0.4, FIG_W-0.4], [y, y], color=color, lw=lw, alpha=alpha, zorder=2)


# ═════════════════════════════════════════════════════════════════════════════
#  TITLE
# ═════════════════════════════════════════════════════════════════════════════
ax.text(FIG_W/2, 19.55, "SkillBridge AI — System Architecture",
    ha="center", va="center", fontsize=24, fontweight="bold", color=WHITE, zorder=10)
ax.text(FIG_W/2, 19.1, "DATA 298B  ·  Team 04  ·  Spring 2026",
    ha="center", va="center", fontsize=11, color=GRAY, zorder=10)
ax.plot([1, FIG_W-1], [18.78, 18.78], color=NEON, lw=1.5, alpha=0.35)

# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 0 — USER ACTIONS
# ═════════════════════════════════════════════════════════════════════════════
section(ax, 0.4, 17.3, FIG_W-0.8, 1.3, DIMGRAY, "USER ACTIONS", alpha=0.1)

user_actions = [
    ("Resume Upload", NEON),
    ("Role Selection", TEAL),
    ("View Dashboard", PURPLE),
    ("Quiz / Interview", GREEN),
    ("Job Search", AMBER),
    ("Export Roadmap", PINK),
]
uw = 3.8
ug = (FIG_W - 0.8 - len(user_actions)*uw) / (len(user_actions)+1)
for i, (lbl, clr) in enumerate(user_actions):
    ux = 0.4 + ug + i*(uw+ug)
    rbox(ax, ux, 17.5, uw, 0.82, clr, lbl, lsize=10.5, r=0.18, lw=1.5, fill=PANEL2)

# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 1 — NEXT.JS FRONTEND
# ═════════════════════════════════════════════════════════════════════════════
section(ax, 0.4, 13.8, FIG_W-0.8, 3.3, NEON, "LAYER 1   —   NEXT.JS 15 FRONTEND  (Port 3000)")

# Connect user → frontend (center arrow)
for i, (_, clr) in enumerate(user_actions):
    ux = 0.4 + ug + i*(uw+ug) + uw/2
    arw(ax, ux, 17.5, ux, 17.08, color=clr, lw=1.2, size=10)

fe_pages = [
    ("/ Home",       "CinematicHeroBg\nFramer Motion",    NEON),
    ("/dashboard\nSkills & Gaps", "Skill cards\nGap analysis", PURPLE),
    ("/dashboard\nRoadmap",       "Timeline view\nProgress tracker", AMBER),
    ("/dashboard\nInterview",     "Flashcards  +\n15Q Quiz / 80%", GREEN),
    ("/dashboard\nJobs",          "Live job listings\n4 API sources", TEAL),
    ("/analytics",                "6 charts\nModel comparison", PINK),
]
pw = 4.0
pg = (FIG_W - 0.8 - len(fe_pages)*pw) / (len(fe_pages)+1)
for i, (lbl, sub, clr) in enumerate(fe_pages):
    px = 0.4 + pg + i*(pw+pg)
    rbox(ax, px, 15.68, pw, 1.3, clr, lbl, sub, lsize=10, ssize=8.5, r=0.22)

# Zustand + Proxy bar
rbox(ax, 0.6, 14.05, 10.5, 0.55, PURPLE,
     "Zustand Store  (localStorage)  —  gapResult  ·  roadmap  ·  user  ·  skills",
     lsize=9, r=0.18, lw=1.4)
rbox(ax, 11.5, 14.05, 16.1, 0.55, NEON,
     "/api/*  &  /static/*  proxied  →  FastAPI backend  (no CORS issues)",
     lsize=9, r=0.18, lw=1.4)

# ═════════════════════════════════════════════════════════════════════════════
#  BIG ARROW  FRONTEND → BACKEND
# ═════════════════════════════════════════════════════════════════════════════
arw(ax, FIG_W/2, 13.8, FIG_W/2, 13.42, color=NEON, lw=3.0, size=18)
alabel(ax, FIG_W/2 + 2.2, 13.6, "HTTPS / JSON", NEON, fs=9.5)

# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 2 — FASTAPI BACKEND
# ═════════════════════════════════════════════════════════════════════════════
section(ax, 0.4, 10.0, FIG_W-0.8, 3.25, PURPLE, "LAYER 2   —   FASTAPI BACKEND  (Port 8000)")

api_routes = [
    ("POST /resume\n/upload",   "PDF → GLiNER\n→ Mistral NER",  NEON),
    ("POST /skills\n/analyze",  "Gap analysis\n35 role profiles", TEAL),
    ("POST /roadmap\n/generate","Nemotron 253B\n+ RAG context",  PURPLE),
    ("GET /jobs\n/search",      "4-source scraper\nasyncio.gather", AMBER),
    ("GET /quiz\n/questions",   "Qwen3 235B\n15 MCQs",          GREEN),
    ("GET /insight\n/market",   "DeepSeek R1\nRAG + trends",    TEAL),
    ("POST /auth\n/login",      "JWT + bcrypt\n+ Sessions DB",  PINK),
]
rw = (FIG_W - 1.5) / len(api_routes) - 0.12
rx0 = 0.55
for i, (lbl, sub, clr) in enumerate(api_routes):
    rbox(ax, rx0 + i*(rw+0.12), 11.6, rw, 1.35, clr, lbl, sub,
         lsize=9.5, ssize=8, r=0.2)

# Services bar
rbox(ax, 0.6, 10.22, 27.0, 0.58, DIMGRAY,
     "Services:   llm.py  (4 model routers)   ·   rag.py  (ChromaDB)   ·   "
     "jobs_fetcher.py  ·   pdf_parser.py   ·   skill_analyzer.py   ·   roadmap_builder.py",
     lsize=9, r=0.18, lw=1.2)

# ═════════════════════════════════════════════════════════════════════════════
#  4 DIVERGING ARROWS  BACKEND → DATA LAYER
# ═════════════════════════════════════════════════════════════════════════════
targets = [
    (3.8,   9.9, C:=TEAL),
    (9.5,   9.9, C:=AMBER),
    (17.5,  9.9, C:=NEON),
    (24.2,  9.9, C:=GREEN),
]
colors_b = [TEAL, AMBER, NEON, GREEN]
labels_b = ["ORM", "RAG", "LLM API", "Jobs API"]
tx = [3.8, 9.5, 17.5, 24.2]
for x, clr, lbl in zip(tx, colors_b, labels_b):
    ax.plot([FIG_W/2, x], [10.0, 9.25], color=clr, lw=1.8, linestyle="--", alpha=0.55, zorder=4)
    arw(ax, x, 9.25, x, 9.05, color=clr, lw=1.8, size=12)
    alabel(ax, x, 9.38, lbl, clr, fs=8)

# ═════════════════════════════════════════════════════════════════════════════
#  LAYER 3 — DATA / AI STORES  (4 big columns)
# ═════════════════════════════════════════════════════════════════════════════
section(ax, 0.4, 1.2, FIG_W-0.8, 7.65, BORDER, "LAYER 3   —   DATA  ·  AI  ·  DEPLOYMENT", alpha=0.06)

COL_W = 5.9
COL_H = 6.7
COL_GAP = 0.6
COL_X = [0.55, 0.55 + COL_W + COL_GAP,
          0.55 + 2*(COL_W + COL_GAP),
          0.55 + 3*(COL_W + COL_GAP)]
COL_Y = 1.45

# ── Column 1: PostgreSQL ──────────────────────────────────────────────────────
rbox(ax, COL_X[0], COL_Y, COL_W, COL_H, TEAL,
     "PostgreSQL\n(Neon Cloud)", lsize=14, r=0.3, fill=PANEL)

pg_items = [
    ("users",               "email · xp · badges · avatar"),
    ("sessions",            "refresh_token · expires_at"),
    ("roadmaps",            "role · skills · roadmap_json · model"),
    ("user_progress",       "completed_steps · quiz_scores"),
    ("quiz_questions",      "options · correct_index · skill_tag"),
    ("jobs",                "title · company · salary · source"),
    ("evaluation_runs",     "model_name · metrics JSON"),
]
row_h = 0.58
for i, (k, v) in enumerate(pg_items):
    ry = COL_Y + COL_H - 1.05 - i*row_h
    bg = "#0E1A2E" if i % 2 == 0 else "#101F38"
    p = mpatches.Rectangle((COL_X[0]+0.1, ry-0.02), COL_W-0.2, row_h-0.06,
        facecolor=bg, edgecolor="none", zorder=4)
    ax.add_patch(p)
    ax.text(COL_X[0]+0.25, ry+row_h/2-0.04, k, ha="left", va="center",
        fontsize=8.5, color=TEAL, fontweight="bold", zorder=5)
    ax.text(COL_X[0]+COL_W-0.15, ry+row_h/2-0.04, v, ha="right", va="center",
        fontsize=7.8, color=GRAY, zorder=5)

ax.text(COL_X[0]+COL_W/2, COL_Y+0.35,
    "SQLAlchemy async  ·  asyncpg driver  ·  Alembic migrations",
    ha="center", va="center", fontsize=7.8, color=GRAY, zorder=5)

# ── Column 2: ChromaDB + RAG ─────────────────────────────────────────────────
rbox(ax, COL_X[1], COL_Y, COL_W, COL_H, AMBER,
     "ChromaDB\n(Vector Store + RAG)", lsize=14, r=0.3, fill=PANEL)

chroma_items = [
    ("skill_resources",     "200+ skill→course embeddings"),
    ("job_descriptions",    "Job skill requirement embeddings"),
    ("interview_questions", "Q&A embeddings for retrieval"),
    ("Embed model",         "all-MiniLM-L6-v2"),
    ("Retrieval",           "Top-3 cosine similarity per skill"),
    ("Injection",           "Prepended to every LLM prompt"),
]
for i, (k, v) in enumerate(chroma_items):
    ry = COL_Y + COL_H - 1.05 - i*row_h
    bg = "#0E1A2E" if i % 2 == 0 else "#101F38"
    p = mpatches.Rectangle((COL_X[1]+0.1, ry-0.02), COL_W-0.2, row_h-0.06,
        facecolor=bg, edgecolor="none", zorder=4)
    ax.add_patch(p)
    ax.text(COL_X[1]+0.25, ry+row_h/2-0.04, k, ha="left", va="center",
        fontsize=8.5, color=AMBER, fontweight="bold", zorder=5)
    ax.text(COL_X[1]+COL_W-0.15, ry+row_h/2-0.04, v, ha="right", va="center",
        fontsize=7.8, color=GRAY, zorder=5)

ax.text(COL_X[1]+COL_W/2, COL_Y+0.35,
    "Seeded at startup  ·  grounds LLMs in real resources",
    ha="center", va="center", fontsize=7.8, color=GRAY, zorder=5)

# ── Column 3: 4 LLMs ──────────────────────────────────────────────────────────
rbox(ax, COL_X[2], COL_Y, COL_W, COL_H, NEON,
     "OpenRouter API\n4 Specialized LLMs (Free)", lsize=14, r=0.3, fill=PANEL)

llms = [
    ("Nemotron Ultra 253B", "Roadmap generation\nLoRA fine-tuned schema",   NEON,   "nvidia/llama-3.1-nemotron-ultra-253b-v1:free"),
    ("Mistral Small 24B",   "Skill extraction\n2nd-pass NER",               PURPLE, "mistralai/mistral-small-3.2-24b-instruct:free"),
    ("DeepSeek R1 671B",    "Market insight + RAG\nChain-of-thought MoE",   TEAL,   "deepseek/deepseek-r1:free"),
    ("Qwen3 235B",          "Interview Qs + Quiz\n15-MCQ generation",       AMBER,  "qwen/qwen3-235b-a22b:free"),
]
lh = 1.38
for i, (name, role, clr, mid) in enumerate(llms):
    ly = COL_Y + COL_H - 0.92 - i*lh
    lp = FancyBboxPatch((COL_X[2]+0.15, ly-lh+0.08), COL_W-0.3, lh-0.1,
        boxstyle="round,pad=0,rounding_size=0.15",
        linewidth=1.4, edgecolor=clr, facecolor=PANEL2, zorder=4)
    ax.add_patch(lp)
    ax.text(COL_X[2]+0.35, ly-0.22, name, ha="left", va="center",
        fontsize=9.5, fontweight="bold", color=clr, zorder=5)
    for j, rl in enumerate(role.split("\n")):
        ax.text(COL_X[2]+0.35, ly-0.58-j*0.32, rl, ha="left", va="center",
            fontsize=8, color=GRAY, zorder=5)
    ax.text(COL_X[2]+COL_W-0.2, ly-0.55, mid, ha="right", va="center",
        fontsize=6.5, color=clr, style="italic", alpha=0.75, zorder=5)

ax.text(COL_X[2]+COL_W/2, COL_Y+0.32,
    "Fallback chain: OpenRouter  →  Secondary LLM  →  Ollama local",
    ha="center", va="center", fontsize=7.5, color=GRAY, zorder=5)

# ── Column 4: Deployment + GLiNER ────────────────────────────────────────────
rbox(ax, COL_X[3], COL_Y, COL_W, COL_H, GREEN,
     "Deployment\n& Local ML", lsize=14, r=0.3, fill=PANEL)

dep_items = [
    ("GLiNER v0.5", "Local NER · 10 entity types\nPre-warmed at startup · 0 API cost", GREEN),
    ("LoRA Fine-Tune", "rank=16 · alpha=32 · <1% params\nLoss 2.8→0.4 in 500 steps", TEAL),
    ("Dockerfile.backend", "Python 3.11 · uvicorn 2 workers\nHEALTHCHECK /api/health", NEON),
    ("Dockerfile.frontend", "Node 20 · next build standalone\n2-stage minimal image", PURPLE),
    ("docker-compose.yml", "postgres + backend + frontend\ndocker compose up --build", AMBER),
]
dh = 1.22
for i, (title, detail, clr) in enumerate(dep_items):
    dy = COL_Y + COL_H - 0.88 - i*dh
    dp = FancyBboxPatch((COL_X[3]+0.15, dy-dh+0.1), COL_W-0.3, dh-0.12,
        boxstyle="round,pad=0,rounding_size=0.14",
        linewidth=1.3, edgecolor=clr, facecolor=PANEL2, zorder=4)
    ax.add_patch(dp)
    ax.text(COL_X[3]+0.35, dy-0.2, title, ha="left", va="center",
        fontsize=9.5, fontweight="bold", color=clr, zorder=5)
    for j, dl in enumerate(detail.split("\n")):
        ax.text(COL_X[3]+0.35, dy-0.52-j*0.3, dl, ha="left", va="center",
            fontsize=8, color=GRAY, zorder=5)

# ═════════════════════════════════════════════════════════════════════════════
#  BOTTOM STATS BAR
# ═════════════════════════════════════════════════════════════════════════════
stats = [
    ("5 Models",    "Nemotron 253B · Mistral 24B\nDeepSeek R1 · Qwen3 235B · GLiNER", NEON),
    ("8 DB Tables", "users · sessions · roadmaps\nprogress · quiz · jobs · eval", TEAL),
    ("9 Metrics",   "ROUGE-1/L · Structure · Richness\nBERTScore · FactScore · AR · CP · CR", AMBER),
    ("4 Job APIs",  "Remotive · Jobicy\nThe Muse · Adzuna", GREEN),
    ("6 Charts",    "bar · radar · scatter\ntraining_loss · modern · comparison", PINK),
    ("Docker",      "backend + frontend\n+ postgres compose", PURPLE),
]
sw = (FIG_W - 1.0) / len(stats)
for i, (title, detail, clr) in enumerate(stats):
    sx = 0.5 + i*sw
    sp = FancyBboxPatch((sx+0.05, 0.08), sw-0.1, 1.0,
        boxstyle="round,pad=0,rounding_size=0.18",
        linewidth=1.5, edgecolor=clr, facecolor=PANEL, zorder=3)
    ax.add_patch(sp)
    ax.text(sx+sw/2, 0.73, title, ha="center", va="center",
        fontsize=11, fontweight="bold", color=clr, zorder=5)
    for j, dl in enumerate(detail.split("\n")):
        ax.text(sx+sw/2, 0.44-j*0.22, dl, ha="center", va="center",
            fontsize=7.5, color=GRAY, zorder=5)

# ═════════════════════════════════════════════════════════════════════════════
#  SAVE
# ═════════════════════════════════════════════════════════════════════════════
out = "/Users/drashtibhingradiya/Desktop/SkillBridge_System_Architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved -> {out}   ({int(FIG_W*DPI)} x {int(FIG_H*DPI)} px)")
