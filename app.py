import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import ALL_ROLES, ROLE_SKILLS, PROCESSED, MODELS

# ===== Plotly theme constants =====
PLOT_BG = "#071227"
PAPER_BG = "rgba(0,0,0,0)"
FONT_CLR = "#EAF2FF"
GRID_CLR = "rgba(148,163,184,0.16)"

st.set_page_config(page_title="SkillBridge AI", page_icon="🎯", layout="wide")

# ===== Global Styling =====
st.markdown("""
<style>
/* ===== APP BACKGROUND ===== */
html, body, [data-testid="stAppViewContainer"], .stApp, .main {
    background:
        radial-gradient(circle at top, rgba(37, 99, 235, 0.16), transparent 26%),
        linear-gradient(180deg, #020617 0%, #031127 45%, #020617 100%) !important;
    color: #e5edff !important;
}

/* Main spacing */
.main .block-container {
    padding-top: 1.8rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 96%;
}

/* Remove white Streamlit header areas */
header, [data-testid="stHeader"], [data-testid="stToolbar"] {
    background: transparent !important;
}

/* Generic text */
html, body, p, span, div, label, small {
    color: #dbe7ff;
}

/* ===== TITLES ===== */
.main-title {
    font-size: 5.5rem;
    font-weight: 1000;
    text-align: center;
    letter-spacing: 2px;
    line-height: 1.04;
    margin-bottom: 0.1rem;
    background: linear-gradient(90deg, #22d3ee, #60a5fa, #818cf8, #c084fc, #f472b6);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glowFlow 7s ease infinite;
    text-shadow: 0 0 18px rgba(96,165,250,0.22);
}

.sub-title {
    text-align: center;
    font-size: 1.08rem;
    color: #b7c8ea !important;
    margin-top: -6px;
    margin-bottom: 18px;
    letter-spacing: 0.6px;
}

/* ===== DIVIDERS ===== */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, #4f46e5, #22d3ee, transparent) !important;
    opacity: 0.85;
}

/* ===== SECTION HEADERS ===== */
.section-hdr {
    font-size: 1.45rem;
    font-weight: 800;
    margin-top: 1.35rem;
    margin-bottom: 0.75rem;
    padding: 12px 16px;
    border-left: 5px solid #5b6dfb;
    border-radius: 14px;
    background: linear-gradient(90deg, rgba(255,255,255,0.045), rgba(255,255,255,0.01));
    color: #f8fbff !important;
    box-shadow: 0 0 14px rgba(91,109,251,0.10);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020817 0%, #071427 40%, #031120 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.18);
}

section[data-testid="stSidebar"] * {
    color: #dbe7ff !important;
}

section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] div {
    color: #c4d4f6 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] strong {
    color: #f8fbff !important;
}

/* ===== LABELS ===== */
label, .stSelectbox label, .stTextArea label, .stSlider label {
    color: #dce8ff !important;
    font-weight: 650 !important;
}

/* ===== INPUTS ===== */
.stTextArea textarea,
.stTextInput input,
.stNumberInput input,
.stDateInput input,
div[data-baseweb="select"] > div {
    background: rgba(8, 18, 38, 0.96) !important;
    color: #f8fbff !important;
    border: 1px solid rgba(99,102,241,0.30) !important;
    border-radius: 12px !important;
}

/* Placeholder */
textarea::placeholder,
input::placeholder {
    color: #8ea6cc !important;
    opacity: 1 !important;
}

/* ===== SELECTBOX DROPDOWN ===== */
ul[role="listbox"] {
    background: #071227 !important;
    border: 1px solid rgba(99,102,241,0.35) !important;
    border-radius: 10px !important;
}

li[role="option"] {
    background: #071227 !important;
    color: #e8f0ff !important;
}

li[role="option"]:hover {
    background: rgba(99,102,241,0.22) !important;
    color: #ffffff !important;
}

li[aria-selected="true"] {
    background: rgba(99,102,241,0.34) !important;
    color: #ffffff !important;
}

/* ===== SLIDER ===== */
.stSlider [data-baseweb="slider"] {
    color: #7c5cff !important;
}

/* ===== BUTTONS ===== */
.stButton > button,
.stDownloadButton > button {
    background: linear-gradient(90deg, #22d3ee, #4f7df3, #7c5cff) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    box-shadow: 0 0 22px rgba(99,102,241,0.35) !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 28px rgba(124,92,255,0.55) !important;
}

/* ===== LINK BUTTONS (fix white job buttons) ===== */
a[data-testid="stLinkButton"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 2.8rem !important;
    width: 100% !important;
    background: linear-gradient(90deg, #0f1e3c, #13264b) !important;
    color: #eaf2ff !important;
    border: 1px solid rgba(99,102,241,0.28) !important;
    border-radius: 12px !important;
    text-decoration: none !important;
    box-shadow: 0 0 12px rgba(34,211,238,0.06) !important;
}

a[data-testid="stLinkButton"]:hover {
    background: linear-gradient(90deg, #13264b, #1b2f5e) !important;
    color: #ffffff !important;
    border: 1px solid rgba(124,92,255,0.45) !important;
}

/* ===== METRIC CARDS ===== */
div[data-testid="metric-container"] {
    background: linear-gradient(180deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02)) !important;
    border: 1px solid rgba(148,163,184,0.14) !important;
    padding: 16px !important;
    border-radius: 16px !important;
    box-shadow: 0 0 12px rgba(34,211,238,0.05) !important;
}

div[data-testid="metric-container"] label,
div[data-testid="metric-container"] [data-testid="stMetricLabel"],
div[data-testid="metric-container"] [data-testid="stMetricLabel"] * {
    color: #bcd0f3 !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricValue"],
div[data-testid="metric-container"] [data-testid="stMetricValue"] * {
    color: #f8fbff !important;
    font-size: 1.65rem !important;
    font-weight: 900 !important;
    opacity: 1 !important;
}

div[data-testid="metric-container"] [data-testid="stMetricDelta"],
div[data-testid="metric-container"] [data-testid="stMetricDelta"] * {
    color: #a5f3fc !important;
    opacity: 1 !important;
}

/* ===== TABS ===== */
button[data-baseweb="tab"] {
    color: #b7c8ea !important;
    background: transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #f8fbff !important;
    border-bottom: 2px solid #6366f1 !important;
}

/* ===== EXPANDERS ===== */
details {
    background: transparent !important;
}

summary {
    background: rgba(8, 18, 38, 0.96) !important;
    color: #f8fbff !important;
    border: 1px solid rgba(99,102,241,0.18) !important;
    border-radius: 12px !important;
}

.streamlit-expanderHeader {
    background: rgba(8, 18, 38, 0.96) !important;
    color: #f8fbff !important;
    border-radius: 12px !important;
}

.streamlit-expanderContent,
details > div {
    background: transparent !important;
    color: #dbe7ff !important;
}

/* ===== DATAFRAMES / TABLES ===== */
div[data-testid="stDataFrame"] {
    background: #071227 !important;
    border: 1px solid rgba(99,102,241,0.16) !important;
    border-radius: 12px !important;
}

div[data-testid="stDataFrame"] * {
    color: #e7efff !important;
}

table {
    background: #071227 !important;
    color: #e7efff !important;
}

thead tr th {
    background: #0c1a34 !important;
    color: #f8fbff !important;
}

tbody tr td {
    background: #071227 !important;
    color: #e7efff !important;
}

/* ===== ALERTS ===== */
div[data-baseweb="notification"] {
    background: #071227 !important;
    color: #eef4ff !important;
    border: 1px solid rgba(99,102,241,0.18) !important;
}

/* ===== CODE ===== */
code, pre {
    background: #071227 !important;
    color: #e6eeff !important;
}

/* ===== PLOTLY CONTAINER ===== */
[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(148,163,184,0.10);
    border-radius: 14px;
    padding: 6px;
}

/* ===== MARKDOWN TEXT ===== */
.stMarkdown, .stMarkdown p, .stMarkdown li {
    color: #dbe7ff !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #04101f;
}
::-webkit-scrollbar-thumb {
    background: rgba(99,102,241,0.45);
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(99,102,241,0.70);
}

/* ===== ANIMATION ===== */
@keyframes glowFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">AI DRIVEN CAREER MENTOR</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-title">Interactive Career Intelligence Website • For all deterministic and goal oriented individuals</p>',
    unsafe_allow_html=True,
)
st.divider()


def apply_dark_chart(fig, show_x_grid=True, show_y_grid=True):
    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_CLR),
        legend=dict(font=dict(color=FONT_CLR)),
        margin=dict(l=20, r=20, t=60, b=20),
    )
    fig.update_xaxes(showgrid=show_x_grid, gridcolor=GRID_CLR, zeroline=False, color=FONT_CLR)
    fig.update_yaxes(showgrid=show_y_grid, gridcolor=GRID_CLR, zeroline=False, color=FONT_CLR)
    return fig


# ── INPUT ──
c1, c2 = st.columns([1, 2])
with c1:
    target_role = st.selectbox("🎯 Target Role", ALL_ROLES)
with c2:
    user_input = st.text_area(
        "💡 Your Skills (comma-separated)",
        placeholder="Python, SQL, Git, Excel...",
        height=80
    )

c3, c4, c5 = st.columns(3)
with c3:
    months = st.selectbox("📅 Roadmap", [1, 2, 3, 4, 6], index=2)
with c4:
    n_qs = st.slider("📝 Questions", 5, 20, 10)
with c5:
    n_proj = st.slider("🏗️ Projects", 3, 7, 5)

st.divider()

run = st.button("⚡ Analyze & Generate AI Career Plan", type="primary", use_container_width=True)

if run and user_input.strip():
    user_skills = [s.strip() for s in user_input.split(",") if s.strip()]

    # ══ SECTION 1: SKILL GAP ══
    st.markdown('<p class="section-hdr">📊 1. Skill Gap Analysis (GLiNER + DeepSeek V3)</p>', unsafe_allow_html=True)

    with st.spinner("Analyzing skills..."):
        from models.model1_skills import SkillGapAnalyzer, JobMarketAnalyzer
        gap = SkillGapAnalyzer().analyze(target_role, user_skills)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Readiness", f"{gap['readiness_pct']}%")
    c2.metric("Gap", f"{gap['gap_pct']}%")
    c3.metric("Have", len(gap["matched"]))
    c4.metric("Need", len(gap["gaps"]))

    color_map = {
        "Critical": "#ef4444",
        "Important": "#f59e0b",
        "Emerging 2025": "#10b981"
    }

    if gap["gaps"]:
        df_gaps = pd.DataFrame(gap["gaps"])
        fig = px.bar(
            df_gaps,
            x="importance_score",
            y="skill",
            color="category",
            orientation="h",
            title=f"Missing Skills for {target_role} (Learn Top First)",
            color_discrete_map=color_map
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), height=max(400, len(df_gaps) * 32))
        apply_dark_chart(fig, show_x_grid=True, show_y_grid=False)
        st.plotly_chart(fig, use_container_width=True)

    ca, cb = st.columns(2)

    with ca:
        cd = gap["category_chart"]
        fig = go.Figure([
            go.Bar(name="✅ Have", x=cd["categories"], y=cd["have"], marker_color="#10b981"),
            go.Bar(name="❌ Need", x=cd["categories"], y=cd["need"], marker_color="#ef4444")
        ])
        fig.update_layout(barmode="group", title="By Category", height=320)
        apply_dark_chart(fig, show_x_grid=False, show_y_grid=True)
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        if gap["gaps"]:
            ic = pd.DataFrame(gap["gaps"])["category"].value_counts()
            fig = px.pie(
                values=ic.values,
                names=ic.index,
                title="Gap Distribution",
                color=ic.index,
                color_discrete_map=color_map
            )
            fig.update_traces(textfont_color=FONT_CLR)
            fig.update_layout(
                paper_bgcolor=PAPER_BG,
                plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_CLR),
                legend=dict(font=dict(color=FONT_CLR)),
                margin=dict(l=20, r=20, t=60, b=20),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 Detailed Breakdown", expanded=True):
        t1, t2 = st.tabs(["❌ Need (Priority)", "✅ Have"])

        with t1:
            if gap["gaps"]:
                st.dataframe(
                    pd.DataFrame(gap["gaps"])[["skill", "category", "importance_score"]]
                    .rename(columns={"skill": "Skill", "category": "Priority", "importance_score": "Score"}),
                    hide_index=True,
                    use_container_width=True
                )

        with t2:
            if gap["matched"]:
                st.dataframe(
                    pd.DataFrame(gap["matched"])[["skill", "category"]]
                    .rename(columns={"skill": "Skill", "category": "Category"}),
                    hide_index=True,
                    use_container_width=True
                )

    with st.expander("📈 Job Market Analysis"):
        with st.spinner("AI analyzing market..."):
            st.markdown(JobMarketAnalyzer().analyze(target_role, user_skills, gap))

    missing_names = [s["skill"] for s in gap["gaps"]]

    # ══ SECTION 2: INTERVIEW ══
    st.divider()
    st.markdown('<p class="section-hdr">📝 2. Interview Questions – Nemotron 3 Nano</p>', unsafe_allow_html=True)

    with st.spinner(f"Generating {n_qs} questions..."):
        from models.model2_interview import InterviewQuestionGenerator
        questions = InterviewQuestionGenerator().generate(target_role, missing_names + user_skills, n_qs)

    if questions:
        for i, q in enumerate(questions, 1):
            d = q.get("difficulty", "Medium")
            icon = {"Easy": "🟢", "Medium": "🟡", "Hard": "🔴"}.get(d, "⚪")
            with st.expander(f"{icon} Q{i}. {q.get('question', '')}", expanded=(i <= 3)):
                st.markdown(f"**Difficulty:** {d} | **Category:** {q.get('category', '')}")
                st.markdown(f"**Skills:** {', '.join(q.get('skills_tested', []))}")
                for pt in q.get("answer_outline", []):
                    st.markdown(f"- {pt}")

    # ══ SECTION 3: PROJECTS ══
    st.divider()
    st.markdown('<p class="section-hdr">🏗️ 3. Resume Projects – Qwen3-8B</p>', unsafe_allow_html=True)

    with st.spinner(f"Generating {n_proj} projects..."):
        from models.model3_projects import ProjectRecommender
        projects = ProjectRecommender().generate(target_role, user_skills, missing_names, n_proj)

    for i, p in enumerate(projects, 1):
        d = p.get("difficulty", "Intermediate")
        icon = {"Beginner": "🟢", "Intermediate": "🟡", "Advanced": "🔴"}.get(d, "⚪")
        with st.expander(f"{icon} Project {i}: {p.get('title', '')}", expanded=(i <= 2)):
            st.markdown(f"**Resume Line:** *{p.get('one_liner', '')}*")
            st.markdown(f"**Description:** {p.get('description', '')}")
            st.markdown(f"**Tech Stack:** {', '.join(p.get('tech_stack', []))}")
            for feat in p.get("features", []):
                st.markdown(f"- {feat}")
            st.markdown(f"**Time:** {p.get('time_estimate', 'N/A')} | **Level:** {d}")
            if p.get("recruiter_appeal"):
                st.success(f"💡 {p['recruiter_appeal']}")

    # ══ SECTION 4: ROADMAP ══
    st.divider()
    st.markdown(f'<p class="section-hdr">🗺️ 4. {months}-Month Roadmap – Nemotron 3 Super</p>', unsafe_allow_html=True)

    variant = st.selectbox(
        "Model",
        [
            "⚡ Offline Template",
            "📋 Nemotron Nano (FREE)",
            "🏆 Nemotron Super (FREE)",
            "🔬 Nemotron Super FINE-TUNED"
        ],
        index=3
    )

    with st.spinner("Generating roadmap..."):
        from models.model5_roadmap import (
            BaselineRoadmap,
            NemotronNanoRoadmap,
            NemotronSuperRoadmap,
            FineTunedNemotronRoadmap,
            _template,
        )

        if "Offline" in variant:
            roadmap = _template(target_role, user_skills, missing_names, months)
        elif "Nano" in variant:
            try:
                roadmap = NemotronNanoRoadmap().generate(target_role, user_skills, missing_names, months)
            except Exception:
                roadmap = _template(target_role, user_skills, missing_names, months)
                st.warning("Nemotron Nano API timed out — showing template fallback")
        elif "FINE" in variant:
            try:
                roadmap = FineTunedNemotronRoadmap().generate(target_role, user_skills, missing_names, months)
            except Exception:
                roadmap = _template(target_role, user_skills, missing_names, months)
                st.warning("Fine-tuned API timed out — showing template fallback")
        else:
            try:
                roadmap = NemotronSuperRoadmap().generate(target_role, user_skills, missing_names, months)
            except Exception:
                roadmap = _template(target_role, user_skills, missing_names, months)
                st.warning("Nemotron Super API timed out — showing template fallback")

    st.markdown(roadmap, unsafe_allow_html=True)

    # ══ SECTION 5: JOB LINKS ══
    st.divider()
    st.markdown(f'<p class="section-hdr">🔗 5. Apply for {target_role} Jobs</p>', unsafe_allow_html=True)

    role_encoded = target_role.replace(" ", "%20")
    cols = st.columns(4)
    cols[0].link_button("🔗 LinkedIn Jobs", f"https://www.linkedin.com/jobs/search/?keywords={role_encoded}", use_container_width=True)
    cols[1].link_button("🔗 Indeed", f"https://www.indeed.com/jobs?q={role_encoded}", use_container_width=True)
    cols[2].link_button("🔗 Glassdoor", f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={role_encoded}", use_container_width=True)
    cols[3].link_button("🔗 ZipRecruiter", f"https://www.ziprecruiter.com/jobs-search?search={role_encoded}", use_container_width=True)

    # ══ LEARNING TIMELINE ══
    if missing_names:
        st.divider()
        st.markdown('<p class="section-hdr">📅 Learning Timeline</p>', unsafe_allow_html=True)

        weeks = months * 4
        spw = max(1, len(missing_names) // weeks)
        tl = [{"Skill": s, "Week": min(i // spw + 1, weeks)} for i, s in enumerate(missing_names)]

        fig = px.bar(
            pd.DataFrame(tl),
            x="Week",
            y="Skill",
            orientation="h",
            title="Schedule",
            color="Week",
            color_continuous_scale="Viridis"
        )
        fig.update_layout(height=max(350, len(missing_names) * 25), yaxis=dict(autorange="reversed"))
        apply_dark_chart(fig, show_x_grid=True, show_y_grid=False)
        st.plotly_chart(fig, use_container_width=True)

elif run:
    st.warning("Enter your skills to get started!")

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🤖 5 Models")
    for _, v in MODELS.items():
        st.caption(f"**{v['name']}**\n{v['task']}\n*{v['cost']}*")

    st.divider()
    st.markdown("### 💾 Database")

    try:
        from database import get_db_stats
        stats = get_db_stats()
        if stats.get("status") == "connected":
            st.success("PostgreSQL ✅")
            for k, v in stats.items():
                if k != "status":
                    st.caption(f"{k}: {v}")
        else:
            st.warning("DB not connected")
    except Exception:
        st.info("DB module loading...")

    st.divider()

    if st.button("📈 Evaluation"):
        p = PROCESSED / "evaluation_report_latest.json"
        if p.exists():
            r = json.loads(p.read_text())
            for mn, md in r.get("models", {}).items():
                with st.expander(mn):
                    for vn, vm in md.get("results", {}).items():
                        st.caption(f"**{vn}**")
                        for k, v in vm.items():
                            if isinstance(v, float):
                                st.caption(f"{k}: {v:.3f}")
        else:
            st.info("Run: python run_pipeline.py --data")