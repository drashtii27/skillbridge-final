"""
SkillBridge AI – Configuration
5 MODELS (all FREE 2025-2026):
  M1: GLiNER v0.5 – Skill Extraction (local, HuggingFace)
  M2: NVIDIA Nemotron 3 Nano – Interview Questions (FREE via OpenRouter)
  M3: DeepSeek V3 – Skill Gap Analysis (FREE 5M tokens)
  M4: Qwen3-8B via Ollama – Project Recommendations (local FREE)
  M5: NVIDIA Nemotron 3 Super – Roadmap Generation (FREE via OpenRouter)
      + 3 sub-variants for comparison: Template | Nemotron Nano | Nemotron Super
"""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"; RAW = DATA / "raw"; PROCESSED = DATA / "processed"
FINETUNE = DATA / "fine_tune"; CACHE = ROOT / "model_cache"
for d in [RAW, PROCESSED, FINETUNE, CACHE]: d.mkdir(parents=True, exist_ok=True)

# ── API Keys (ALL FREE) ───────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_BASE_URL = OLLAMA_URL  # alias for backward compatibility
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Scraper keys (pre-filled)
ADZUNA_ID = os.getenv("ADZUNA_APP_ID", "bc0754c6")
ADZUNA_KEY = os.getenv("ADZUNA_APP_KEY", "4e7f378b51e4ac0674961026ca34bcb2")
STACKEX_KEY = os.getenv("STACKEXCHANGE_KEY", "rl_5CmhWZzwRgTsy37jkUfGmPD44")

# Database
PG_URL = os.getenv("PG_URL", "postgresql+psycopg2://neondb_owner:npg_BjLKXvME3U2e@ep-empty-shape-ai5rrofa-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require")

# ── 5 Model Definitions (2025-2026) ───────────────────────────
MODELS = {
    "M1_SKILL_EXTRACT": {
        "name": "GLiNER v0.5 (Knowledgator 2024)",
        "type": "Zero-shot NER (Transformer)",
        "hf_id": "knowledgator/gliner-multitask-large-v0.5",
        "cost": "FREE (local)",
        "task": "Extract technical skills from job descriptions",
    },
    "M2_INTERVIEW": {
        "name": "NVIDIA Nemotron 3 Nano 30B (2026)",
        "type": "Hybrid Mamba-Transformer MoE",
        "api": "openrouter",
        "model_id": "nvidia/nemotron-3-nano-30b-a3b:free",
        "cost": "FREE ($0/token via OpenRouter)",
        "task": "Generate role-specific interview questions",
    },
    "M3_SKILL_GAP": {
        "name": "DeepSeek V3 (2025-2026)",
        "type": "MoE Transformer (671B total, 37B active)",
        "api": "deepseek",
        "model_id": "deepseek-chat",
        "cost": "FREE (5M tokens on signup)",
        "task": "Analyze skill gap with importance classification",
    },
    "M4_PROJECTS": {
        "name": "Qwen3-8B via Ollama (Alibaba 2025)",
        "type": "Dense Transformer with thinking mode",
        "api": "ollama",
        "model_id": "qwen3:8b",
        "cost": "FREE (runs locally)",
        "task": "Recommend resume-worthy projects",
    },
    "M5_ROADMAP": {
        "name": "NVIDIA Nemotron 3 Super 120B (2026)",
        "type": "Hybrid Mamba-Transformer MoE (120B/12B active)",
        "api": "openrouter",
        "model_id": "nvidia/nemotron-3-super-120b-a12b:free",
        "cost": "FREE ($0/token via OpenRouter)",
        "task": "Generate detailed career roadmaps (main model)",
        "variants": {
            "baseline": "Template (offline, no API)",
            "normal": "Nemotron 3 Nano (FREE)",
            "proper": "Nemotron 3 Super (FREE, best)",
        },
    },
}

NOISE = {
    "communication","networking","teamwork","leadership","problem solving",
    "time management","critical thinking","adaptability","creativity",
    "interpersonal skills","self-motivated","detail-oriented","multitasking",
    "organizational skills","work ethic","positive attitude","flexibility",
    "dependability","professionalism","integrity","collaboration",
    "verbal communication","written communication","presentation skills",
    "conflict resolution","decision making","emotional intelligence",
    "stress management","negotiation","persuasion","active listening",
    "empathy","patience","resilience","initiative","accountability",
}

# ══════════════════════════════════════════════════════════════
#  ROLE → SKILLS 2025-2026 (all domains)
# ══════════════════════════════════════════════════════════════
ROLE_SKILLS = {
    "Software Engineer": {
        "critical": ["DSA (Trees, Graphs, DP, Binary Search)","Python","Java","System Design","SQL (Joins, Indexing, CTEs)","Git","REST APIs"],
        "important": ["TypeScript","React/Next.js","Docker","Kubernetes","AWS/GCP/Azure","CI/CD","Microservices"],
        "emerging_2025": ["LLM Integration","RAG Architecture","Vector Databases","Rust","AI-assisted Coding"],
    },
    "Frontend Developer": {
        "critical": ["JavaScript/TypeScript","React 19+","Next.js 15","HTML5/CSS3","Responsive Design"],
        "important": ["Tailwind CSS","Zustand/Jotai","Testing (Vitest/Playwright)","Vite"],
        "emerging_2025": ["Server Components","AI-powered UI (v0)","View Transitions API"],
    },
    "Backend Developer": {
        "critical": ["Python (FastAPI/Django)","Java (Spring Boot)","SQL & DB Design","REST/GraphQL APIs","Docker"],
        "important": ["Go/Rust","Kafka/RabbitMQ","Redis","Kubernetes","gRPC"],
        "emerging_2025": ["Event-Driven Architecture","Serverless","OpenTelemetry"],
    },
    "Data Scientist": {
        "critical": ["Python","Statistics & Probability","Pandas/NumPy","Scikit-learn","SQL","ML Algorithms"],
        "important": ["PyTorch/TensorFlow","Feature Engineering","A/B Testing","Tableau/Power BI"],
        "emerging_2025": ["LLM Fine-tuning (LoRA)","Transformers","MLOps (MLflow/W&B)"],
    },
    "Data Analyst": {
        "critical": ["SQL (Window Functions, CTEs, Joins)","Excel (Advanced)","Python (Pandas)","Tableau/Power BI","Statistics"],
        "important": ["R","Google Analytics 4","dbt","Looker"],
        "emerging_2025": ["AI-augmented Analytics","Databricks SQL","Data Storytelling"],
    },
    "Data Engineer": {
        "critical": ["Python","SQL","Apache Spark","Apache Airflow","Cloud (AWS/GCP)"],
        "important": ["Kafka","Snowflake/BigQuery","Docker","Terraform","dbt"],
        "emerging_2025": ["Apache Iceberg","Flink Streaming","Data Mesh","DuckDB"],
    },
    "ML Engineer": {
        "critical": ["Python","PyTorch","HuggingFace Transformers","MLOps","Docker/Kubernetes"],
        "important": ["Model Serving (vLLM)","Feature Stores","W&B","CUDA"],
        "emerging_2025": ["LoRA/PEFT Fine-tuning","RAG (LangChain)","RLHF/DPO"],
    },
    "DevOps Engineer": {
        "critical": ["Linux/Bash","Docker","Kubernetes","CI/CD (GitHub Actions)","Terraform"],
        "important": ["AWS/GCP/Azure","Prometheus/Grafana","Ansible","Helm"],
        "emerging_2025": ["Platform Engineering","GitOps (ArgoCD)","eBPF"],
    },
    "Cybersecurity Analyst": {
        "critical": ["Network Security","SIEM (Splunk)","Incident Response","Vulnerability Assessment","NIST/ISO 27001"],
        "important": ["Penetration Testing","MITRE ATT&CK","Cloud Security","Python"],
        "emerging_2025": ["AI Threat Detection","Zero Trust","K8s Security"],
    },
    "Business Analyst": {
        "critical": ["SQL","Requirements (BRD/FRD)","BPMN","Excel (Advanced)","Stakeholder Management"],
        "important": ["Tableau/Power BI","Jira/Confluence","User Stories","Agile/Scrum"],
        "emerging_2025": ["AI-assisted Requirements","Process Mining","Low-code Platforms"],
    },
    "Product Manager": {
        "critical": ["Product Strategy","User Research","SQL/Analytics","PRD Writing","A/B Testing"],
        "important": ["Figma","Jira","OKRs","Competitive Analysis"],
        "emerging_2025": ["AI Product Management","Product-Led Growth"],
    },
    "Project Manager": {
        "critical": ["Project Planning","Agile/Scrum","Stakeholder Communication","Risk Management","Budget"],
        "important": ["Jira/MS Project","PMP Certification","Resource Management"],
        "emerging_2025": ["AI-assisted PM","Hybrid Agile"],
    },
    "Marketing Manager": {
        "critical": ["Digital Marketing Strategy","Google Analytics 4","Campaign Management","Brand Strategy"],
        "important": ["HubSpot/Salesforce","SEO/SEM","Social Media","Email Marketing"],
        "emerging_2025": ["AI Content Generation","Marketing Mix Modeling"],
    },
    "Marketing Analyst": {
        "critical": ["SQL","Google Analytics 4","Excel","Statistical Analysis","Tableau/Power BI"],
        "important": ["Python/R","A/B Testing","Attribution Modeling"],
        "emerging_2025": ["Marketing Mix Modeling","Predictive CLV"],
    },
    "Civil Engineer": {
        "critical": ["AutoCAD","Civil 3D","Structural Analysis (SAP2000)","Revit (BIM)","Primavera P6"],
        "important": ["Geotechnical Engineering","Hydraulics","Surveying","GIS"],
        "emerging_2025": ["AI Structural Design","Digital Twins","Drone Surveying"],
    },
    "Mechanical Engineer": {
        "critical": ["SolidWorks/CATIA","AutoCAD","ANSYS (FEA/CFD)","Thermodynamics","GD&T"],
        "important": ["MATLAB/Simulink","Manufacturing Processes","3D Printing"],
        "emerging_2025": ["Generative Design (AI)","Digital Twins","EV Powertrain"],
    },
    "Electrical Engineer": {
        "critical": ["Circuit Design","PCB Design (Altium)","MATLAB","Power Systems","Embedded C/C++"],
        "important": ["VHDL/Verilog","PLC Programming","Control Systems"],
        "emerging_2025": ["IoT System Design","FPGA for AI","EV Charging Infrastructure"],
    },
    "Nurse": {
        "critical": ["Patient Assessment","Medication Administration","EHR (Epic/Cerner)","BLS/ACLS","Vital Signs"],
        "important": ["IV Therapy","Wound Care","Triage","Infection Control"],
        "emerging_2025": ["Telehealth Nursing","AI Clinical Decision Support"],
    },
    "UX Designer": {
        "critical": ["Figma","User Research","Wireframing & Prototyping","Usability Testing","Design Systems"],
        "important": ["Information Architecture","Accessibility (WCAG)","Interaction Design"],
        "emerging_2025": ["AI-assisted Design","Spatial Design (VR/AR)"],
    },
    "HR Manager": {
        "critical": ["HRIS (Workday/BambooHR)","Recruitment","Employee Relations","Compensation & Benefits","Labor Law"],
        "important": ["Performance Management","Training & Development","HR Analytics"],
        "emerging_2025": ["AI Recruiting Tools","People Analytics"],
    },
    "Financial Analyst": {
        "critical": ["Financial Modeling (DCF, LBO)","Excel (VBA)","Financial Statements","Valuation"],
        "important": ["Bloomberg Terminal","Capital IQ","SQL","Python"],
        "emerging_2025": ["AI Financial Modeling","ESG Analysis"],
    },
    "Accountant": {
        "critical": ["GAAP/IFRS","General Ledger","Financial Reporting","Tax Preparation","ERP (SAP)"],
        "important": ["Excel (Advanced)","Audit","CPA Certification"],
        "emerging_2025": ["AI Bookkeeping","Cloud Accounting"],
    },
    "Graphic Designer": {
        "critical": ["Adobe Photoshop","Adobe Illustrator","Typography","Brand Identity"],
        "important": ["Adobe InDesign","Color Theory","Canva"],
        "emerging_2025": ["AI Image Generation","Motion Graphics","3D (Blender)"],
    },
    "Supply Chain Analyst": {
        "critical": ["Demand Forecasting","Inventory Management","SQL","Excel","ERP (SAP)"],
        "important": ["Tableau/Power BI","Supply Chain Optimization"],
        "emerging_2025": ["AI Demand Sensing","Digital Twins"],
    },
    "Technical Writer": {
        "critical": ["Technical Documentation","Markdown","API Documentation","Information Architecture"],
        "important": ["Git","Docs-as-Code","Diagramming"],
        "emerging_2025": ["AI-assisted Writing","Interactive Docs"],
    },
    "Research Scientist": {
        "critical": ["Research Methodology","Statistical Analysis (R/Python)","Scientific Writing","Experiment Design"],
        "important": ["Domain Expertise","Grant Writing"],
        "emerging_2025": ["AI-assisted Research","Computational Methods"],
    },
}

ALL_ROLES = sorted(ROLE_SKILLS.keys())

def get_role_skills(role):
    rd = ROLE_SKILLS.get(role, {})
    s = []
    for v in rd.values(): s.extend(v)
    return s
