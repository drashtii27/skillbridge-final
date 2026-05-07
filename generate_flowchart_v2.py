"""
SkillBridge AI — Simple Clean Flowchart  v2
Big text, lots of whitespace, no clutter.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

FIG_W, FIG_H = 18, 30
DPI = 160
fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("#06091C")
ax.set_facecolor("#06091C")
ax.set_xlim(0, FIG_W)
ax.set_ylim(0, FIG_H)
ax.axis("off")

BG    = "#06091C"
PANEL = "#0C1428"

NEON   = "#38BDF8"
PURPLE = "#A78BFA"
GREEN  = "#4ADE80"
AMBER  = "#FBBF24"
TEAL   = "#2DD4BF"
PINK   = "#F472B6"
RED    = "#F87171"
WHITE  = "#FFFFFF"
GRAY   = "#94A3B8"

CX = FIG_W / 2   # spine center


# ─── helpers ──────────────────────────────────────────────────────────────────

def node(cx, cy, w, h, color, title, sub=None, fill=PANEL, lw=2.8, r=0.3):
    x, y = cx - w/2, cy - h/2
    p = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={r}",
        linewidth=lw, edgecolor=color, facecolor=fill, zorder=3)
    ax.add_patch(p)
    # glow ring
    g = FancyBboxPatch((x-.1, y-.1), w+.2, h+.2,
        boxstyle=f"round,pad=0,rounding_size={r+.12}",
        linewidth=.8, edgecolor=color, facecolor="none", zorder=2, alpha=.18)
    ax.add_patch(g)
    ty = cy + (.25 if sub else 0)
    t = ax.text(cx, ty, title, ha="center", va="center",
        fontsize=18, fontweight="bold", color=WHITE, zorder=5)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground=BG)])
    if sub:
        ax.text(cx, cy - .32, sub, ha="center", va="center",
            fontsize=13, color=GRAY, zorder=5)


def oval_node(cx, cy, w, h, color, text):
    from matplotlib.patches import Ellipse
    e = Ellipse((cx, cy), w, h, linewidth=2.8, edgecolor=color,
        facecolor=color + "28", zorder=3)
    ax.add_patch(e)
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=18, fontweight="bold", color=WHITE, zorder=5)


def diamond_node(cx, cy, w, h, color, text):
    hw, hh = w/2, h/2
    pts = [(cx, cy+hh), (cx+hw, cy), (cx, cy-hh), (cx-hw, cy)]
    poly = plt.Polygon(pts, closed=True, linewidth=2.8,
        edgecolor=color, facecolor=color + "28", zorder=3)
    ax.add_patch(poly)
    ax.text(cx, cy, text, ha="center", va="center",
        fontsize=16, fontweight="bold", color=WHITE, zorder=5)


def arr(x1, y1, x2, y2, color, lw=2.5, size=18):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
            mutation_scale=size, connectionstyle="arc3,rad=0"),
        zorder=6)


def line_seg(x1, y1, x2, y2, color, lw=2.2):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, zorder=3,
        solid_capstyle="round")


def arr_label(cx, cy, text, color):
    ax.text(cx, cy, text, ha="center", va="center", fontsize=11,
        fontweight="bold", color=color, zorder=7,
        bbox=dict(boxstyle="round,pad=0.3", facecolor=BG,
                  edgecolor=color, linewidth=1.2, alpha=.95))


def step_num(num, cx, cy, color):
    c = plt.Circle((cx, cy), .28, color=color, zorder=7)
    ax.add_patch(c)
    ax.text(cx, cy, str(num), ha="center", va="center",
        fontsize=11, fontweight="bold", color=BG, zorder=8)


# ─────────────────────────────────────────────────────────────────────────────
# TITLE
# ─────────────────────────────────────────────────────────────────────────────
ax.text(CX, 29.4, "SkillBridge AI — System Flowchart",
    ha="center", fontsize=24, fontweight="bold", color=WHITE, zorder=10)
ax.text(CX, 28.85, "DATA 298B  ·  Team 04  ·  Spring 2026",
    ha="center", fontsize=13, color=GRAY, zorder=10)
ax.plot([1.5, FIG_W-1.5], [28.55, 28.55], color=NEON, lw=1.0, alpha=.3)

# ─────────────────────────────────────────────────────────────────────────────
# 1  USER
# ─────────────────────────────────────────────────────────────────────────────
step_num(1, 2.5, 27.8, NEON)
oval_node(CX, 27.8, 7.0, 1.0, NEON, "User  (Browser)")
arr(CX, 27.3, CX, 26.72, NEON)

# ─────────────────────────────────────────────────────────────────────────────
# 2  DECISION
# ─────────────────────────────────────────────────────────────────────────────
step_num(2, 2.5, 26.2, NEON)
diamond_node(CX, 26.2, 5.8, 1.1, NEON, "How to start?")

# Left — PDF branch
line_seg(CX - 2.9, 26.2, CX - 5.5, 26.2, NEON)
arr(CX - 5.5, 26.2, CX - 5.5, 25.12, NEON)
arr_label(CX - 4.0, 26.42, "Upload Resume", NEON)

# Right — Manual branch
line_seg(CX + 2.9, 26.2, CX + 5.5, 26.2, AMBER)
arr(CX + 5.5, 26.2, CX + 5.5, 25.12, AMBER)
arr_label(CX + 4.0, 26.42, "Select Role", AMBER)

# ─────────────────────────────────────────────────────────────────────────────
# 3  BRANCHES
# ─────────────────────────────────────────────────────────────────────────────
node(CX - 5.5, 24.5, 5.5, 1.1, NEON,
     "PDF Parser",
     "pdfplumber  +  OCR fallback")

node(CX + 5.5, 24.5, 5.5, 1.1, AMBER,
     "Role Selector",
     "35 career role profiles")

# Merge back to center
line_seg(CX - 5.5, 23.95, CX - 5.5, 23.45, NEON)
line_seg(CX + 5.5, 23.95, CX + 5.5, 23.45, AMBER)
line_seg(CX - 5.5, 23.45, CX + 5.5, 23.45, GREEN)
arr(CX, 23.45, CX, 23.05, GREEN, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 4  SKILL EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────
step_num(3, 2.5, 22.42, GREEN)
node(CX, 22.42, 12.0, 1.15, GREEN,
     "Skill Extraction",
     "GLiNER NER (local)  +  Mistral Small 24B  →  deduplicated skill list")
arr(CX, 21.84, CX, 21.22, AMBER, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 5  GAP ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
step_num(4, 2.5, 20.6, AMBER)
node(CX, 20.6, 12.0, 1.15, AMBER,
     "Skill Gap Analysis",
     "User skills  vs  35 role benchmarks  →  missing_skills [ ]")
arr(CX, 20.02, CX, 19.4, TEAL, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 6  RAG
# ─────────────────────────────────────────────────────────────────────────────
step_num(5, 2.5, 18.78, TEAL)
node(CX, 18.78, 12.0, 1.15, TEAL,
     "ChromaDB RAG",
     "Retrieve top-3 learning resources  →  inject into LLM prompt")
arr(CX, 18.2, CX, 17.55, RED, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 7  NEMOTRON — MAIN MODEL
# ─────────────────────────────────────────────────────────────────────────────
step_num(6, 2.5, 16.92, RED)
node(CX, 16.92, 13.5, 1.35, RED,
     "NVIDIA Nemotron Ultra 253B",
     "Generates 12-week roadmap  ·  LoRA fine-tuned  ·  Week / Resources / Project / Checkpoint",
     fill="#150810", lw=3.2)
arr(CX, 16.24, CX, 15.62, PURPLE, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 8  FASTAPI — PERSIST
# ─────────────────────────────────────────────────────────────────────────────
step_num(7, 2.5, 15.0, PURPLE)
node(CX, 15.0, 12.0, 1.15, PURPLE,
     "FastAPI Backend  —  Save & Route",
     "Roadmap → PostgreSQL  ·  XP awarded  ·  Badges checked")

# Fan-out line
line_seg(CX, 14.42, CX, 13.95, PURPLE)
BXLIST = [3.0, 7.3, 10.7, 15.0]
line_seg(BXLIST[0], 13.95, BXLIST[-1], 13.95, "#334155")
for bx in BXLIST:
    arr(bx, 13.95, bx, 13.58, PURPLE, lw=2.0, size=13)

# ─────────────────────────────────────────────────────────────────────────────
# 8b  4 FEATURE BOXES
# ─────────────────────────────────────────────────────────────────────────────
BW, BH = 3.8, 3.2
B_Y = 12.0
B_COLORS = [AMBER, TEAL, GREEN, PINK]
B_TITLES = ["Roadmap\nDashboard", "Job Market\nIntelligence", "Quiz\n(15 MCQs  /  80%)", "Interview\nPrep"]
B_DETAILS = [
    ["12-week timeline", "XP + Badges", "OpenNote export", "JSON download"],
    ["Remotive  ·  Jobicy", "The Muse  ·  Adzuna", "Concurrent fetch", "DeepSeek R1 671B"],
    ["Qwen3 235B", "30 sec / question", "Weak skill cards", "Resource links"],
    ["Qwen3 235B", "Flashcard Q&A", "Easy / Med / Hard", "Answer outlines"],
]

for bx, bc, bt, bd in zip(BXLIST, B_COLORS, B_TITLES, B_DETAILS):
    node(bx, B_Y, BW, BH, bc, bt, fill=PANEL, lw=2.2)
    for i, item in enumerate(bd):
        ax.text(bx, B_Y + 0.9 - i * 0.65, f"• {item}",
            ha="center", va="center", fontsize=11, color=GRAY, zorder=5)

# Merge back
MERGE_Y = 10.32
for bx, bc in zip(BXLIST, B_COLORS):
    line_seg(bx, B_Y - BH/2, bx, MERGE_Y, bc, lw=1.8)
line_seg(BXLIST[0], MERGE_Y, BXLIST[-1], MERGE_Y, "#334155")
arr(CX, MERGE_Y, CX, 9.92, PURPLE, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 9  DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
step_num(8, 2.5, 9.3, PURPLE)
node(CX, 9.3, 12.0, 1.15, PURPLE,
     "User Dashboard  (Next.js 15)",
     "Roadmap  ·  Jobs  ·  Quiz results  ·  Progress  ·  XP  ·  Badges")
arr(CX, 8.72, CX, 8.12, NEON, size=16)

# ─────────────────────────────────────────────────────────────────────────────
# 10  EXPORT  +  ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
line_seg(CX, 8.12, CX, 7.85, NEON)
line_seg(CX - 3.2, 7.85, CX + 3.2, 7.85, "#334155")
arr(CX - 3.2, 7.85, CX - 3.2, 7.5, NEON, lw=2.0, size=13)
arr(CX + 3.2, 7.85, CX + 3.2, 7.5, PINK, lw=2.0, size=13)

node(CX - 3.2, 6.95, 5.6, 1.1, NEON,
     "Export",
     "OpenNote markdown  ·  JSON")

node(CX + 3.2, 6.95, 5.6, 1.1, PINK,
     "Analytics  /analytics",
     "6 charts  ·  Model comparison")

line_seg(CX - 3.2, 6.4, CX - 3.2, 6.1, NEON)
line_seg(CX + 3.2, 6.4, CX + 3.2, 6.1, PINK)
line_seg(CX - 3.2, 6.1, CX + 3.2, 6.1, "#334155")
arr(CX, 6.1, CX, 5.78, GREEN, size=14)

# ─────────────────────────────────────────────────────────────────────────────
# 11  END
# ─────────────────────────────────────────────────────────────────────────────
oval_node(CX, 5.3, 7.5, 1.0, GREEN, "User achieves career goal")

# ─────────────────────────────────────────────────────────────────────────────
# LEGEND  (compact, bottom)
# ─────────────────────────────────────────────────────────────────────────────
legend = [
    ("Frontend / User", NEON),
    ("Skill Extraction ML", GREEN),
    ("Database / RAG", AMBER),
    ("ChromaDB", TEAL),
    ("LLM / AI Models", RED),
    ("FastAPI / Backend", PURPLE),
    ("Output / Export", PINK),
]
lx = 1.2
ly = 4.1
ax.text(lx, ly + .35, "Legend", fontsize=13, fontweight="bold",
    color=GRAY, zorder=6)
for i, (lbl, clr) in enumerate(legend):
    xi = lx + (i % 4) * 4.1
    yi = ly - (i // 4) * .55
    c = plt.Circle((xi + .18, yi), .14, color=clr, zorder=6)
    ax.add_patch(c)
    ax.text(xi + .44, yi, lbl, fontsize=11, color=GRAY,
        va="center", zorder=6)

# ─────────────────────────────────────────────────────────────────────────────
# KEY STATS BAR
# ─────────────────────────────────────────────────────────────────────────────
stats = [
    ("5 Models", NEON),
    ("8 DB Tables", AMBER),
    ("9 Eval Metrics", GREEN),
    ("4 Job APIs", TEAL),
    ("80% Quiz Pass", PINK),
    ("Docker Ready", PURPLE),
]
sw = (FIG_W - 1.0) / len(stats)
for i, (title, clr) in enumerate(stats):
    sx = .5 + i * sw
    p = FancyBboxPatch((sx + .1, .15), sw - .2, .78,
        boxstyle="round,pad=0,rounding_size=.15",
        linewidth=1.8, edgecolor=clr, facecolor=PANEL, zorder=4)
    ax.add_patch(p)
    ax.text(sx + sw/2, .57, title,
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=clr, zorder=5)

# ─────────────────────────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────────────────────────
out = "/Users/drashtibhingradiya/Desktop/SkillBridge_System_Architecture.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved  {out}")
