"""
SkillBridge AI — Horizontal System Flowchart (PPT-Ready, Huge Text)
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Ellipse

FIG_W, FIG_H = 64, 22
DPI = 280

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
BG = "#F8FAFC"
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

C = {
    "blue":   "#0369A1",
    "purple": "#6D28D9",
    "green":  "#15803D",
    "amber":  "#B45309",
    "teal":   "#0F766E",
    "red":    "#B91C1C",
    "pink":   "#BE185D",
    "dark":   "#0F172A",
    "gray":   "#4B5563",
    "dim":    "#CBD5E1",
    "panel":  "#FFFFFF",
}

CY  = 15.0   # main spine Y
BW  = 7.5    # standard box width
BH  = 4.0    # standard box height


# ── helpers ───────────────────────────────────────────────────────────────────

def box(cx, cy, w, h, color, text, sub="", fs=30):
    x, y = cx - w/2, cy - h/2
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0,rounding_size=0.35",
        linewidth=4.0, edgecolor=color, facecolor=C["panel"], zorder=3))
    ax.add_patch(FancyBboxPatch((x-.1, y-.1), w+.2, h+.2,
        boxstyle="round,pad=0,rounding_size=0.44",
        linewidth=1.0, edgecolor=color, facecolor="none", zorder=2, alpha=.16))
    if sub:
        ax.text(cx, cy + 0.52, text, ha="center", va="center",
            fontsize=fs, fontweight="bold", color=C["dark"], zorder=5)
        ax.text(cx, cy - 0.62, sub, ha="center", va="center",
            fontsize=18, color=C["gray"], zorder=5)
    else:
        ax.text(cx, cy, text, ha="center", va="center",
            fontsize=fs, fontweight="bold", color=C["dark"], zorder=5)


def oval(cx, cy, w, h, color, text, fs=26):
    ax.add_patch(Ellipse((cx, cy), w, h,
        linewidth=4.0, edgecolor=color, facecolor=color+"22", zorder=3))
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=fs, fontweight="bold", color=color, zorder=5)


def diamond(cx, cy, w, h, color, text, fs=24):
    hw, hh = w/2, h/2
    ax.add_patch(plt.Polygon(
        [(cx, cy+hh), (cx+hw, cy), (cx, cy-hh), (cx-hw, cy)],
        closed=True, linewidth=4.0,
        edgecolor=color, facecolor=color+"22", zorder=3))
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=fs, fontweight="bold", color=color, zorder=5)


def card(cx, cy, w, h, color, title, items):
    x, y = cx - w/2, cy - h/2
    r = 0.32
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=3.5, edgecolor=color, facecolor=C["panel"], zorder=3))
    hdr_h = 1.35
    ax.add_patch(FancyBboxPatch((x, y+h-hdr_h), w, hdr_h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=0, edgecolor="none",
        facecolor=color+"30", zorder=4))
    ax.text(cx, y+h-hdr_h/2, title, ha="center", va="center",
        fontsize=22, fontweight="bold", color=color, zorder=5, linespacing=1.2)
    body_top = y + h - hdr_h - 0.28
    body_bot = y + 0.32
    step = (body_top - body_bot) / len(items)
    for i, item in enumerate(items):
        iy = body_top - step * (i + 0.5)
        ax.text(cx, iy, item, ha="center", va="center",
            fontsize=20, color=C["gray"], zorder=5)


def rarr(x1, y1, x2, y2, color, lw=3.2, sz=30):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color,
            lw=lw, mutation_scale=sz,
            connectionstyle="arc3,rad=0"), zorder=6)


def seg(x1, y1, x2, y2, color, lw=3.0):
    ax.plot([x1,x2],[y1,y2], color=color, lw=lw,
        zorder=3, solid_capstyle="round")


def tag(cx, cy, text, color):
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=19, fontweight="bold", color=color, zorder=7,
        bbox=dict(boxstyle="round,pad=0.35", facecolor=C["panel"],
                  edgecolor=color, linewidth=2.0, alpha=.97))


def stepnum(cx, n, color):
    ax.add_patch(plt.Circle((cx, CY + 2.35), .38, color=color, zorder=7))
    ax.text(cx, CY + 2.35, str(n), ha="center", va="center",
        fontsize=18, fontweight="bold", color="#FFFFFF", zorder=8)


# ─── TITLE ────────────────────────────────────────────────────────────────────
ax.text(FIG_W/2, 21.4, "SkillBridge AI — System Architecture",
    ha="center", fontsize=50, fontweight="bold", color=C["dark"])
ax.text(FIG_W/2, 20.55, "DATA 298B  ·  Team 04  ·  Spring 2026",
    ha="center", fontsize=24, color=C["gray"])
ax.plot([1, FIG_W-1], [20.1, 20.1], color=C["blue"], lw=1.4, alpha=.3)

# ─── X COORDINATES ────────────────────────────────────────────────────────────
X1 =  3.5    # User oval
X2 =  9.5    # Decision diamond
X3 = 18.5    # Skill Extraction
X4 = 27.5    # Skill Gap Analysis
X5 = 36.5    # ChromaDB RAG
X6 = 46.5    # Nemotron  (wider)
X7 = 56.5    # FastAPI
X8 = 62.0    # Dashboard

# ─── 1  USER ──────────────────────────────────────────────────────────────────
stepnum(X1, 1, C["blue"])
oval(X1, CY, 6.0, 2.5, C["blue"], "User\n(Browser)", fs=26)
rarr(X1 + 3.0, CY, X2 - 3.5, CY, C["blue"])

# ─── 2  DECISION ──────────────────────────────────────────────────────────────
stepnum(X2, 2, C["blue"])
diamond(X2, CY, 6.5, 2.5, C["blue"], "How to\nstart?", fs=22)

# branch UP — Upload PDF
seg(X2, CY + 1.25, X2, CY + 3.5, C["blue"])
seg(X2, CY + 3.5, X2 + 3.0, CY + 3.5, C["blue"])
rarr(X2 + 3.0, CY + 3.5, X3 - BW/2, CY + 3.5, C["blue"], lw=2.5, sz=22)
tag(X2 + 1.5, CY + 4.0, "Upload PDF", C["blue"])

# branch DOWN — Select Role
seg(X2, CY - 1.25, X2, CY - 3.5, C["amber"])
seg(X2, CY - 3.5, X2 + 3.0, CY - 3.5, C["amber"])
rarr(X2 + 3.0, CY - 3.5, X3 - BW/2, CY - 3.5, C["amber"], lw=2.5, sz=22)
tag(X2 + 1.5, CY - 4.0, "Select Role", C["amber"])

# Merge into left edge of Skill Extraction
rarr(X3 - BW/2, CY + 3.5, X3 - BW/2 + 0.01, CY, C["green"], lw=2.5, sz=20)
rarr(X3 - BW/2, CY - 3.5, X3 - BW/2 + 0.01, CY, C["green"], lw=2.5, sz=20)

# ─── 3  SKILL EXTRACTION ──────────────────────────────────────────────────────
stepnum(X3, 3, C["green"])
box(X3, CY, BW, BH, C["green"], "Skill Extraction",
    sub="GLiNER NER  +  Mistral Small 24B")
rarr(X3 + BW/2, CY, X4 - BW/2, CY, C["amber"])

# ─── 4  SKILL GAP ANALYSIS ────────────────────────────────────────────────────
stepnum(X4, 4, C["amber"])
box(X4, CY, BW, BH, C["amber"], "Skill Gap Analysis",
    sub="vs 35 role benchmarks")
rarr(X4 + BW/2, CY, X5 - BW/2, CY, C["teal"])

# ─── 5  CHROMADB RAG ──────────────────────────────────────────────────────────
stepnum(X5, 5, C["teal"])
box(X5, CY, BW, BH, C["teal"], "ChromaDB RAG",
    sub="Top-3 matches → LLM prompt")
rarr(X5 + BW/2, CY, X6 - 5.0, CY, C["red"])

# ─── 6  NEMOTRON ULTRA 253B ───────────────────────────────────────────────────
stepnum(X6, 6, C["red"])
NW = 9.5
x0, y0 = X6 - NW/2, CY - BH/2
ax.add_patch(FancyBboxPatch((x0, y0), NW, BH,
    boxstyle="round,pad=0,rounding_size=0.38",
    linewidth=5.0, edgecolor=C["red"], facecolor="#FFF1F1", zorder=3))
ax.add_patch(FancyBboxPatch((x0-.11, y0-.11), NW+.22, BH+.22,
    boxstyle="round,pad=0,rounding_size=0.48",
    linewidth=1.2, edgecolor=C["red"], facecolor="none", zorder=2, alpha=.2))
ax.text(X6, CY + 0.52, "NVIDIA Nemotron Ultra 253B",
    ha="center", va="center", fontsize=30,
    fontweight="bold", color=C["red"], zorder=5)
ax.text(X6, CY - 0.62, "Roadmap Gen  ·  LoRA fine-tuned  ·  12-week plan",
    ha="center", va="center", fontsize=18, color=C["gray"], zorder=5)
rarr(X6 + NW/2, CY, X7 - BW/2, CY, C["purple"])

# ─── 7  FASTAPI BACKEND ───────────────────────────────────────────────────────
stepnum(X7, 7, C["purple"])
box(X7, CY, BW, BH, C["purple"], "FastAPI Backend",
    sub="PostgreSQL  ·  Award XP  ·  Badges")
rarr(X7 + BW/2, CY, X8 - 3.5, CY, C["purple"])

# ─── 8  USER DASHBOARD ────────────────────────────────────────────────────────
stepnum(X8, 8, C["purple"])
box(X8, CY, 6.5, BH, C["purple"], "User\nDashboard",
    sub="Jobs · Quiz · Progress", fs=28)

# ─── 4 CARDS (fan down from FastAPI, aligned with spine boxes) ────────────────
CY_CARDS = 7.2
BW_C = 7.5
BH_C = 5.5
BXS = [X3, X4, X5, X6]   # aligned under Skill→Nemotron

BCOLORS = [C["amber"], C["teal"], C["green"], C["pink"]]
BTITLES = ["Roadmap\nDashboard", "Job Market", "Quiz  15 MCQs", "Interview\nPrep"]
BITEMS = [
    ["12-week plan", "XP + Badges", "Export"],
    ["4 Live APIs",  "Real listings", "DeepSeek R1"],
    ["Qwen3 235B",   "80% threshold", "Weak skill links"],
    ["Qwen3 235B",   "Flashcards",    "Q&A outlines"],
]

for bx, bc, bt, bi in zip(BXS, BCOLORS, BTITLES, BITEMS):
    card(bx, CY_CARDS, BW_C, BH_C, bc, bt, bi)

# Fan-out from FastAPI down to trunk
TRUNK_Y  = CY - BH/2 - 1.0          # below spine boxes
CARD_TOP = CY_CARDS + BH_C/2 + 0.1  # top of cards

seg(X7, CY - BH/2, X7, TRUNK_Y, C["purple"])
seg(BXS[0], TRUNK_Y, X7, TRUNK_Y, C["dim"])
for bx, bc in zip(BXS, BCOLORS):
    seg(bx, TRUNK_Y, bx, CARD_TOP, bc, lw=2.5)
    rarr(bx, CARD_TOP, bx, CARD_TOP - 0.01, bc, lw=2.5, sz=20)

# Merge from card bottoms back into FastAPI bottom
MERGE_Y  = CY_CARDS - BH_C/2 - 0.35
for bx, bc in zip(BXS, BCOLORS):
    seg(bx, CY_CARDS - BH_C/2, bx, MERGE_Y, bc, lw=2.0)
seg(BXS[0], MERGE_Y, X7, MERGE_Y, C["dim"])
seg(X7, MERGE_Y, X7, CY - BH/2, C["purple"])

# ─── BOTTOM STATS BAR ─────────────────────────────────────────────────────────
stats = [
    ("5 Models",     C["blue"]),
    ("8 DB Tables",  C["amber"]),
    ("9 Metrics",    C["green"]),
    ("4 Job APIs",   C["teal"]),
    ("Docker Ready", C["purple"]),
]
sw = (FIG_W - 2.0) / len(stats)
for i, (label, clr) in enumerate(stats):
    bx = 1.0 + i * sw
    ax.add_patch(FancyBboxPatch((bx+.12, .15), sw-.24, 1.25,
        boxstyle="round,pad=0,rounding_size=.22",
        linewidth=2.8, edgecolor=clr, facecolor=clr+"18", zorder=4))
    ax.text(bx + sw/2, 0.78, label, ha="center", va="center",
        fontsize=24, fontweight="bold", color=clr, zorder=5)

# ─── SAVE ─────────────────────────────────────────────────────────────────────
out = "/Users/drashtibhingradiya/Desktop/SkillBridge_System_Architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=DPI, bbox_inches="tight",
    facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved  {out}   ({int(FIG_W*DPI)} x {int(FIG_H*DPI)} px)")
