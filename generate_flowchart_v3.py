"""
SkillBridge AI — Minimalist System Flowchart  v3
No overlap. Title top, bullets below. Clean spacing.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

# ── Canvas ────────────────────────────────────────────────────────────────────
FIG_W, FIG_H = 20, 32
DPI = 150

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
BG = "#07091B"
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

# ── Colors ────────────────────────────────────────────────────────────────────
PANEL  = "#0C1530"
NEON   = "#38BDF8"
PURPLE = "#A78BFA"
GREEN  = "#4ADE80"
AMBER  = "#FBBF24"
TEAL   = "#2DD4BF"
PINK   = "#F472B6"
RED    = "#F87171"
WHITE  = "#FFFFFF"
GRAY   = "#94A3B8"
DIM    = "#2D3A52"

CX = FIG_W / 2   # main spine x


# ── Primitives ────────────────────────────────────────────────────────────────

def rbox(cx, cy, w, h, color, title, sub=None, lw=2.6, r=0.28):
    """Rounded box. Title centered in box; sub one line below title."""
    x, y = cx - w/2, cy - h/2
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=lw, edgecolor=color, facecolor=PANEL, zorder=3))
    ax.add_patch(FancyBboxPatch((x-.08, y-.08), w+.16, h+.16,
        boxstyle=f"round,pad=0,rounding_size={r+.1}",
        linewidth=.7, edgecolor=color, facecolor="none",
        zorder=2, alpha=.18))
    ty = cy + (.22 if sub else 0)
    t = ax.text(cx, ty, title, ha="center", va="center",
        fontsize=18, fontweight="bold", color=WHITE, zorder=5)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground=BG)])
    if sub:
        ax.text(cx, cy - .28, sub, ha="center", va="center",
            fontsize=12, color=GRAY, zorder=5)


def card(cx, cy, w, h, color, title, bullets, lw=2.4):
    """Card with title pinned near top and bullets below — no overlap ever."""
    x, y = cx - w/2, cy - h/2
    r = 0.3
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=lw, edgecolor=color, facecolor=PANEL, zorder=3))
    ax.add_patch(FancyBboxPatch((x-.08, y-.08), w+.16, h+.16,
        boxstyle=f"round,pad=0,rounding_size={r+.1}",
        linewidth=.7, edgecolor=color, facecolor="none",
        zorder=2, alpha=.18))
    # Title strip at top
    ax.add_patch(FancyBboxPatch((x, y+h-0.72), w, 0.72,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=0, edgecolor="none", facecolor=color+"33", zorder=4))
    t = ax.text(cx, y + h - 0.36, title, ha="center", va="center",
        fontsize=15, fontweight="bold", color=WHITE, zorder=5)
    t.set_path_effects([pe.withStroke(linewidth=2.5, foreground=BG)])
    # Bullets below title strip
    bullet_start = y + h - 0.88
    spacing = (h - 0.88) / (len(bullets) + 0.5)
    for i, b in enumerate(bullets):
        ax.text(cx, bullet_start - spacing * (i + 0.5), f"• {b}",
            ha="center", va="center", fontsize=12, color=GRAY, zorder=5)


def oval_node(cx, cy, w, h, color, text):
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((cx, cy), w, h, linewidth=2.8,
        edgecolor=color, facecolor=color+"28", zorder=3))
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=17, fontweight="bold", color=WHITE, zorder=5)


def diamond_node(cx, cy, w, h, color, text):
    hw, hh = w/2, h/2
    ax.add_patch(plt.Polygon(
        [(cx, cy+hh), (cx+hw, cy), (cx, cy-hh), (cx-hw, cy)],
        closed=True, linewidth=2.8,
        edgecolor=color, facecolor=color+"28", zorder=3))
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=15, fontweight="bold", color=WHITE, zorder=5)


def arr(x1, y1, x2, y2, color, lw=2.4, size=17):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
            mutation_scale=size, connectionstyle="arc3,rad=0"),
        zorder=6)


def seg(x1, y1, x2, y2, color, lw=2.2):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, zorder=3,
        solid_capstyle="round")


def alabel(cx, cy, text, color, fs=11):
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs,
        fontweight="bold", color=color, zorder=7,
        bbox=dict(boxstyle="round,pad=0.3", facecolor=BG,
                  edgecolor=color, linewidth=1.1, alpha=.95))


def stepnum(n, cx, cy, color):
    ax.add_patch(plt.Circle((cx, cy), .28, color=color, zorder=7))
    ax.text(cx, cy, str(n), ha="center", va="center",
        fontsize=10, fontweight="bold", color=BG, zorder=8)


# ═════════════════════════════════════════════════════════════════════════════
#  TITLE
# ═════════════════════════════════════════════════════════════════════════════
ax.text(CX, 31.35, "SkillBridge AI — System Flowchart",
    ha="center", fontsize=24, fontweight="bold", color=WHITE)
ax.text(CX, 30.78, "DATA 298B  ·  Team 04  ·  Spring 2026",
    ha="center", fontsize=13, color=GRAY)
ax.plot([2, FIG_W-2], [30.48, 30.48], color=NEON, lw=.8, alpha=.3)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 1  — USER
# ═════════════════════════════════════════════════════════════════════════════
stepnum(1, 3.0, 29.65, NEON)
oval_node(CX, 29.65, 7.5, 1.05, NEON, "User  (Browser)")
arr(CX, 29.12, CX, 28.55, NEON)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 2  — HOW TO START?
# ═════════════════════════════════════════════════════════════════════════════
stepnum(2, 3.0, 27.98, NEON)
diamond_node(CX, 27.98, 6.0, 1.15, NEON, "How to start?")

# Left branch
seg(CX-3.0, 27.98, CX-6.5, 27.98, NEON)
arr(CX-6.5, 27.98, CX-6.5, 27.05, NEON, lw=2.0, size=14)
alabel(CX-4.55, 28.22, "Upload PDF", NEON, fs=10)

# Right branch
seg(CX+3.0, 27.98, CX+6.5, 27.98, AMBER)
arr(CX+6.5, 27.98, CX+6.5, 27.05, AMBER, lw=2.0, size=14)
alabel(CX+4.55, 28.22, "Select Role", AMBER, fs=10)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 2a / 2b  — INPUT NODES
# ═════════════════════════════════════════════════════════════════════════════
rbox(CX-6.5, 26.38, 5.8, 1.15, NEON,
     "PDF Parser",
     "pdfplumber  +  OCR fallback")

rbox(CX+6.5, 26.38, 5.8, 1.15, AMBER,
     "Role Selector",
     "35 career role profiles")

# Merge
seg(CX-6.5, 25.80, CX-6.5, 25.35, NEON)
seg(CX+6.5, 25.80, CX+6.5, 25.35, AMBER)
seg(CX-6.5, 25.35, CX+6.5, 25.35, GREEN)
arr(CX, 25.35, CX, 24.95, GREEN, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 3  — SKILL EXTRACTION
# ═════════════════════════════════════════════════════════════════════════════
stepnum(3, 3.0, 24.32, GREEN)
rbox(CX, 24.32, 13.0, 1.18, GREEN,
     "Skill Extraction",
     "GLiNER NER  (local, 0 API cost)   +   Mistral Small 24B  (OpenRouter)")
arr(CX, 23.73, CX, 23.12, AMBER, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 4  — GAP ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
stepnum(4, 3.0, 22.5, AMBER)
rbox(CX, 22.5, 13.0, 1.18, AMBER,
     "Skill Gap Analysis",
     "User skills  vs  35 role benchmarks   →   missing_skills [ ]")
arr(CX, 21.91, CX, 21.3, TEAL, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 5  — RAG
# ═════════════════════════════════════════════════════════════════════════════
stepnum(5, 3.0, 20.68, TEAL)
rbox(CX, 20.68, 13.0, 1.18, TEAL,
     "ChromaDB RAG",
     "Top-3 course matches retrieved   →   injected into LLM system prompt")
arr(CX, 20.09, CX, 19.42, RED, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 6  — NEMOTRON 253B
# ═════════════════════════════════════════════════════════════════════════════
stepnum(6, 3.0, 18.75, RED)
rbox(CX, 18.75, 14.5, 1.45, RED,
     "NVIDIA Nemotron Ultra 253B  —  Roadmap Generator",
     "12-week plan  ·  Week / Resources / Project / Checkpoint  ·  LoRA fine-tuned",
     lw=3.2)
arr(CX, 18.02, CX, 17.38, PURPLE, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 7  — FASTAPI
# ═════════════════════════════════════════════════════════════════════════════
stepnum(7, 3.0, 16.75, PURPLE)
rbox(CX, 16.75, 13.0, 1.18, PURPLE,
     "FastAPI Backend  —  Save & Route",
     "Roadmap  →  PostgreSQL   ·   XP awarded   ·   Badges unlocked")

# Fan out to 4 branches
seg(CX, 16.16, CX, 15.72, PURPLE)
BXS = [3.2, 7.85, 12.15, 16.8]
seg(BXS[0], 15.72, BXS[-1], 15.72, DIM)
for bx in BXS:
    arr(bx, 15.72, bx, 15.38, PURPLE, lw=1.8, size=12)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 7b  — 4 FEATURE CARDS  (title at top, bullets below — NO OVERLAP)
# ═════════════════════════════════════════════════════════════════════════════
BW, BH = 4.1, 4.2
BY = 13.22   # center y of cards

card(BXS[0], BY, BW, BH, AMBER, "Roadmap\nDashboard",
     ["12-week timeline", "XP + Badges", "OpenNote export", "JSON download"])

card(BXS[1], BY, BW, BH, TEAL, "Job Market",
     ["Remotive  ·  Jobicy", "The Muse  ·  Adzuna", "asyncio.gather  (<2s)", "DeepSeek R1 671B"])

card(BXS[2], BY, BW, BH, GREEN, "Quiz  (15 MCQs)",
     ["Qwen3 235B", "80% pass threshold", "Weak skill cards", "Resource links"])

card(BXS[3], BY, BW, BH, PINK, "Interview Prep",
     ["Qwen3 235B", "Flashcard Q&A", "Easy / Med / Hard", "Answer outlines"])

# Merge back
MERGE_Y = 11.1
for bx, bc in zip(BXS, [AMBER, TEAL, GREEN, PINK]):
    seg(bx, BY - BH/2, bx, MERGE_Y, bc, lw=1.6)
seg(BXS[0], MERGE_Y, BXS[-1], MERGE_Y, DIM)
arr(CX, MERGE_Y, CX, 10.68, PURPLE, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 8  — DASHBOARD
# ═════════════════════════════════════════════════════════════════════════════
stepnum(8, 3.0, 10.05, PURPLE)
rbox(CX, 10.05, 13.0, 1.18, PURPLE,
     "User Dashboard  (Next.js 15)",
     "Roadmap  ·  Jobs  ·  Quiz results  ·  Progress  ·  XP  ·  Badges")
arr(CX, 9.46, CX, 8.85, NEON, size=15)

# ═════════════════════════════════════════════════════════════════════════════
#  STEP 9  — EXPORT + ANALYTICS
# ═════════════════════════════════════════════════════════════════════════════
seg(CX, 8.85, CX, 8.55, NEON)
seg(CX-3.5, 8.55, CX+3.5, 8.55, DIM)
arr(CX-3.5, 8.55, CX-3.5, 8.18, NEON, lw=1.9, size=13)
arr(CX+3.5, 8.55, CX+3.5, 8.18, PINK, lw=1.9, size=13)

rbox(CX-3.5, 7.6, 6.0, 1.15, NEON,
     "Export",
     "OpenNote markdown  ·  JSON download")

rbox(CX+3.5, 7.6, 6.0, 1.15, PINK,
     "Analytics",
     "6 charts  ·  4-model comparison  ·  /analytics")

seg(CX-3.5, 7.02, CX-3.5, 6.72, NEON)
seg(CX+3.5, 7.02, CX+3.5, 6.72, PINK)
seg(CX-3.5, 6.72, CX+3.5, 6.72, DIM)
arr(CX, 6.72, CX, 6.35, GREEN, size=14)

# ═════════════════════════════════════════════════════════════════════════════
#  END
# ═════════════════════════════════════════════════════════════════════════════
oval_node(CX, 5.85, 8.0, 1.05, GREEN, "User achieves career goal")

# ═════════════════════════════════════════════════════════════════════════════
#  BOTTOM BAR
# ═════════════════════════════════════════════════════════════════════════════
stats = [
    ("5 Models",      "Nemotron · Mistral · DeepSeek · Qwen3 · GLiNER", NEON),
    ("8 DB Tables",   "users · roadmaps · progress · quiz · jobs…",      AMBER),
    ("9 Metrics",     "ROUGE · BERTScore · FactScore · AR · CP · CR",    GREEN),
    ("4 Job Sources", "Remotive · Jobicy · The Muse · Adzuna",           TEAL),
    ("Docker Ready",  "backend + frontend + postgres compose",           PURPLE),
]
sw = (FIG_W - 1.0) / len(stats)
for i, (title, detail, clr) in enumerate(stats):
    bx = .5 + i * sw
    ax.add_patch(FancyBboxPatch((bx+.1, .15), sw-.2, 1.35,
        boxstyle="round,pad=0,rounding_size=.2",
        linewidth=1.8, edgecolor=clr, facecolor=PANEL, zorder=4))
    ax.text(bx + sw/2, 1.05, title,
        ha="center", va="center", fontsize=13, fontweight="bold",
        color=clr, zorder=5)
    ax.text(bx + sw/2, .58, detail,
        ha="center", va="center", fontsize=9, color=GRAY, zorder=5)

# separator line
ax.plot([.5, FIG_W-.5], [1.62, 1.62], color=DIM, lw=.8, alpha=.5)

# ═════════════════════════════════════════════════════════════════════════════
#  SAVE
# ═════════════════════════════════════════════════════════════════════════════
out = "/Users/drashtibhingradiya/Desktop/SkillBridge_System_Architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved  {out}   ({int(FIG_W*DPI)} x {int(FIG_H*DPI)} px)")
