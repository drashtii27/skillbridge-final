from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/skillbridge"
    secret_key: str = "change-me-in-production-super-secret-key-32chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "nemotron-mini"   # Model 1: Nemotron for roadmap generation

    # OpenRouter model IDs for the other 3 specialized models
    openrouter_api_key: str = ""
    openrouter_model: str = "nvidia/llama-3.1-nemotron-ultra-253b-v1:free"   # Model 1: Roadmap generation
    skill_model: str = "mistralai/mistral-small-3.2-24b-instruct:free"      # Model 2: Skill extraction (LLM fallback)
    insight_model: str = "deepseek/deepseek-r1:free"                         # Model 3: Market insight/RAG
    interview_model: str = "qwen/qwen3-235b-a22b:free"                       # Model 4: Interview & Quiz

    posthog_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"

    adzuna_app_id: str = ""
    adzuna_app_key: str = ""

    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "https://*.vercel.app"]

    chroma_persist_dir: str = "./chroma_db"

    class Config:
        env_file = [".env", "backend/.env"]  # backend/.env last = highest priority
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


BADGES = {
    "resume_uploaded": {"title": "Resume Pioneer", "icon": "📄", "xp": 50, "desc": "Uploaded your first resume"},
    "roadmap_generated": {"title": "Roadmap Starter", "icon": "🗺️", "xp": 100, "desc": "Generated your first roadmap"},
    "quiz_ace": {"title": "Quiz Ace", "icon": "🧠", "xp": 150, "desc": "Scored 80%+ on a quiz"},
    "week_1_done": {"title": "Week 1 Warrior", "icon": "⚔️", "xp": 200, "desc": "Completed Week 1 of roadmap"},
    "job_applied": {"title": "Job Hunter", "icon": "💼", "xp": 75, "desc": "Applied to your first job"},
    "interview_ready": {"title": "Interview Ready", "icon": "🎤", "xp": 100, "desc": "Practiced 10+ interview questions"},
    "streak_3": {"title": "3-Day Streak", "icon": "🔥", "xp": 120, "desc": "Active 3 days in a row"},
    "community_joiner": {"title": "Community Star", "icon": "⭐", "xp": 50, "desc": "Joined a learning community"},
}

ROLE_SKILLS = {
    # ── Tech / Engineering ──────────────────────────────────────────────────
    "Machine Learning Engineer": {
        "critical": ["Python", "PyTorch", "TensorFlow", "scikit-learn", "NumPy", "Pandas", "SQL", "Git"],
        "important": ["MLflow", "Docker", "Kubernetes", "FastAPI", "Spark", "Kafka", "AWS/GCP/Azure", "Airflow"],
        "emerging": ["LangChain", "RAG", "LoRA fine-tuning", "vLLM", "Triton Inference Server", "Rust for ML"],
    },
    "Data Scientist": {
        "critical": ["Python", "SQL", "Statistics", "Pandas", "NumPy", "scikit-learn", "Tableau/Power BI"],
        "important": ["R", "Spark", "Airflow", "A/B Testing", "Causal Inference", "Feature Engineering", "Matplotlib"],
        "emerging": ["AutoML", "Causal ML", "Time Series Forecasting", "Synthetic Data Generation", "DataBricks"],
    },
    "Software Engineer (Backend)": {
        "critical": ["Python/Go/Java/Node.js", "SQL", "REST APIs", "Git", "Docker", "Data Structures & Algorithms"],
        "important": ["PostgreSQL", "Redis", "Kafka", "Kubernetes", "CI/CD", "gRPC", "GraphQL", "System Design"],
        "emerging": ["WebAssembly", "eBPF", "Rust", "Edge Computing", "Deno", "Bun"],
    },
    "Software Engineer (Frontend)": {
        "critical": ["JavaScript", "TypeScript", "React", "CSS", "HTML", "Git", "REST APIs"],
        "important": ["Next.js", "Redux/Zustand", "Testing (Jest/Cypress)", "Webpack/Vite", "Node.js", "GraphQL"],
        "emerging": ["React Server Components", "WebAssembly", "Astro", "SolidJS", "CSS Container Queries", "View Transitions API"],
    },
    "Full Stack Developer": {
        "critical": ["JavaScript", "TypeScript", "React/Next.js", "Node.js", "SQL", "REST APIs", "Git"],
        "important": ["PostgreSQL", "MongoDB", "Docker", "Redis", "Testing", "CI/CD", "Auth (JWT/OAuth)"],
        "emerging": ["Edge Runtime", "Server Actions", "tRPC", "Drizzle ORM", "Bun", "WebSockets"],
    },
    "DevOps / Cloud Engineer": {
        "critical": ["Linux", "Docker", "Kubernetes", "Terraform", "AWS/GCP/Azure", "CI/CD (GitHub Actions)", "Bash/Python"],
        "important": ["Helm", "ArgoCD", "Prometheus/Grafana", "Ansible", "Vault", "Service Mesh (Istio)"],
        "emerging": ["eBPF", "Platform Engineering", "Internal Developer Platforms", "Crossplane", "OpenTelemetry"],
    },
    "Data Engineer": {
        "critical": ["Python", "SQL", "Spark", "Kafka", "Airflow", "dbt", "Data Warehousing (Snowflake/BigQuery)"],
        "important": ["Flink", "Delta Lake/Iceberg", "Docker", "Kubernetes", "Great Expectations", "DBT Cloud"],
        "emerging": ["Apache Paimon", "OpenLineage", "Data Contracts", "Streaming SQL (Flink SQL)"],
    },
    "Cybersecurity Engineer": {
        "critical": ["Network Security", "Linux", "Python", "SIEM tools", "Penetration Testing", "Incident Response", "OWASP"],
        "important": ["Cloud Security (AWS/Azure)", "Terraform", "Zero Trust Architecture", "SOAR", "Threat Modeling"],
        "emerging": ["AI Security (Red-Teaming LLMs)", "Post-Quantum Cryptography", "eBPF for Security", "Confidential Computing"],
    },
    "Mobile Developer (iOS)": {
        "critical": ["Swift", "SwiftUI", "UIKit", "Xcode", "REST APIs", "Git", "CoreData"],
        "important": ["Combine", "TestFlight", "Push Notifications", "App Store Connect", "Firebase", "Core Location"],
        "emerging": ["SwiftData", "VisionOS", "WidgetKit", "App Clips", "Metal"],
    },
    "Mobile Developer (Android)": {
        "critical": ["Kotlin", "Jetpack Compose", "Android SDK", "REST APIs", "Git", "MVVM"],
        "important": ["Room DB", "Retrofit", "Coroutines", "Firebase", "Play Console", "Material Design"],
        "emerging": ["Kotlin Multiplatform", "Wear OS", "ML Kit", "Android 14 APIs"],
    },
    "Game Developer": {
        "critical": ["Unity/Unreal Engine", "C#/C++", "3D Math", "Physics Simulation", "Git", "Game Design Fundamentals"],
        "important": ["Shader Programming", "Networking (multiplayer)", "Mobile Game Optimization", "Blender (basic 3D)", "Cinemachine"],
        "emerging": ["MetaHuman", "Lumen/Nanite (Unreal 5)", "AI NPCs (LLM integration)", "WebGPU Games"],
    },
    "Embedded Systems Engineer": {
        "critical": ["C", "C++", "Microcontrollers (ARM/AVR)", "RTOS", "Debugging (JTAG/SWD)", "Hardware Protocols (I2C/SPI/UART)"],
        "important": ["Python (scripting)", "Linux Kernel", "FPGA (Verilog/VHDL)", "PCB Reading", "CAN Bus", "Bare-Metal Programming"],
        "emerging": ["Rust for Embedded", "RISC-V", "TinyML", "Matter/Thread (IoT)"],
    },
    "Network Engineer": {
        "critical": ["Cisco IOS", "TCP/IP", "BGP/OSPF", "VLAN", "Firewall Configuration", "Network Security", "Linux"],
        "important": ["Python (network automation)", "Ansible", "SD-WAN", "Wireshark", "VPN", "AWS VPC", "Load Balancers"],
        "emerging": ["Network as Code", "SASE", "eBPF Networking", "P4 Programming"],
    },
    "Blockchain Developer": {
        "critical": ["Solidity", "Ethereum", "Smart Contracts", "Web3.js/ethers.js", "JavaScript/TypeScript", "Hardhat/Foundry"],
        "important": ["IPFS", "DeFi Protocols", "NFT Standards (ERC-721/1155)", "Layer 2 (Arbitrum/Optimism)", "OpenZeppelin"],
        "emerging": ["ZK-Proofs", "Account Abstraction (ERC-4337)", "Cross-chain Bridges", "Move (Aptos/Sui)"],
    },
    "AI Research Engineer": {
        "critical": ["Python", "PyTorch", "Mathematics (Linear Algebra, Calculus)", "Research Paper Reading", "NumPy", "Transformers (HuggingFace)"],
        "important": ["CUDA/GPU Programming", "Distributed Training", "MLflow", "LaTeX", "JAX", "DeepSpeed"],
        "emerging": ["RLHF/DPO", "Mixture of Experts", "State Space Models (Mamba)", "Mechanistic Interpretability"],
    },
    "Robotics Engineer": {
        "critical": ["ROS/ROS2", "Python", "C++", "Kinematics", "SLAM", "Computer Vision (OpenCV)", "Control Theory"],
        "important": ["Gazebo Simulation", "TensorFlow/PyTorch", "Embedded Systems", "3D Printing (prototyping)", "LiDAR/Sensor Fusion"],
        "emerging": ["Foundation Models for Robotics", "Sim-to-Real Transfer", "Soft Robotics", "Neuromorphic Computing"],
    },
    "QA / SDET": {
        "critical": ["Python/Java", "Selenium/Playwright", "API Testing (Postman)", "CI/CD", "Test Case Design", "SQL", "Git"],
        "important": ["Performance Testing (k6/JMeter)", "BDD (Cucumber)", "Mobile Testing (Appium)", "Docker", "Jira"],
        "emerging": ["AI-assisted Testing", "Shift-left Testing", "Contract Testing (Pact)", "Chaos Engineering"],
    },

    # ── Product / Design ─────────────────────────────────────────────────────
    "Product Manager": {
        "critical": ["Product Strategy", "User Research", "Agile/Scrum", "Data Analysis", "Stakeholder Management", "Roadmapping"],
        "important": ["SQL basics", "Figma", "A/B Testing", "OKRs", "Go-to-Market", "Pricing Strategy"],
        "emerging": ["AI Product Management", "PLG (Product-Led Growth)", "Jobs-to-be-Done Framework"],
    },
    "UI/UX Designer": {
        "critical": ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems", "Accessibility"],
        "important": ["Motion Design (After Effects)", "Framer", "Design Thinking", "Usability Testing", "Copywriting"],
        "emerging": ["AI-Assisted Design", "3D Web (Spline)", "Voice UI", "Spatial Computing (visionOS)", "Generative UI"],
    },
    "Graphic Designer": {
        "critical": ["Adobe Photoshop", "Adobe Illustrator", "InDesign", "Typography", "Color Theory", "Brand Identity"],
        "important": ["After Effects", "Figma", "Print Production", "Photography basics", "Video Editing"],
        "emerging": ["AI Image Generation (Midjourney/DALL-E)", "Motion Graphics", "3D Design (Blender)", "Generative Art"],
    },

    # ── Business / Finance ────────────────────────────────────────────────────
    "Business Analyst": {
        "critical": ["Requirements Gathering", "SQL", "Excel/Google Sheets", "Process Mapping (BPMN)", "Stakeholder Communication", "Agile"],
        "important": ["Tableau/Power BI", "Jira", "SWOT Analysis", "Wireframing (Figma basics)", "UAT", "Python basics"],
        "emerging": ["AI-Driven Analytics", "No-Code Automation (Zapier)", "Digital Twin Modeling"],
    },
    "Financial Analyst": {
        "critical": ["Excel (advanced)", "Financial Modeling", "Valuation (DCF/Comps)", "Accounting", "SQL", "Bloomberg Terminal"],
        "important": ["Python (pandas)", "Power BI/Tableau", "VBA", "R", "CFA Concepts", "Risk Analysis"],
        "emerging": ["LLM-Assisted Research", "Alternative Data Analysis", "ESG Metrics", "Crypto/DeFi Finance"],
    },
    "Marketing Manager": {
        "critical": ["Digital Marketing", "SEO/SEM", "Google Analytics", "Email Marketing", "Content Strategy", "Social Media"],
        "important": ["HubSpot/Salesforce CRM", "A/B Testing", "Paid Ads (Meta/Google)", "Copywriting", "Marketing Attribution"],
        "emerging": ["AI Content Tools (ChatGPT/Jasper)", "Influencer Marketing", "Web3 Marketing", "Community-Led Growth"],
    },
    "Operations Manager": {
        "critical": ["Project Management", "Process Optimization", "Data Analysis", "Excel", "Supply Chain Basics", "Leadership"],
        "important": ["ERP Systems (SAP/Oracle)", "Six Sigma", "SQL", "Tableau", "Vendor Management", "KPI Tracking"],
        "emerging": ["AI-Driven Forecasting", "RPA (UiPath/Automation Anywhere)", "Digital Operations", "Sustainability Ops"],
    },
    "Sales Engineer": {
        "critical": ["Technical Product Knowledge", "Solution Selling", "CRM (Salesforce)", "Communication", "Demo Skills", "API/Integration basics"],
        "important": ["SQL", "Python scripting", "Cloud Platforms (AWS/Azure)", "Proposal Writing", "Competitive Analysis"],
        "emerging": ["AI Sales Tools", "PLG (Product-Led Sales)", "RevOps", "No-code Demos"],
    },
    "HR Manager": {
        "critical": ["Talent Acquisition", "Employee Relations", "HRIS (Workday/BambooHR)", "Labor Law", "Performance Management", "Onboarding"],
        "important": ["Data Analytics (Excel/SQL)", "Compensation Benchmarking", "DEI Initiatives", "Learning & Development", "ATS Systems"],
        "emerging": ["People Analytics", "AI-Assisted Recruiting", "Remote Team Culture", "Skills-Based Hiring"],
    },

    # ── Healthcare ────────────────────────────────────────────────────────────
    "Registered Nurse": {
        "critical": ["Patient Assessment", "Medication Administration", "IV Therapy", "Electronic Health Records (EHR)", "BLS/ACLS", "Clinical Documentation"],
        "important": ["Telemetry Monitoring", "Wound Care", "Care Coordination", "HIPAA Compliance", "Patient Education", "Phlebotomy"],
        "emerging": ["Telehealth", "AI-Assisted Diagnosis Tools", "Remote Patient Monitoring", "Genomics Basics"],
    },
    "Healthcare Data Analyst": {
        "critical": ["SQL", "Python/R", "EHR Data (Epic/Cerner)", "HIPAA", "Statistical Analysis", "Tableau/Power BI"],
        "important": ["ICD-10 Coding", "HL7/FHIR", "Machine Learning basics", "Excel", "Data Governance", "Clinical Outcomes Research"],
        "emerging": ["NLP for Clinical Notes", "Predictive Models for Readmission", "AI Diagnostics", "Real-World Evidence"],
    },

    # ── Engineering (Non-Software) ────────────────────────────────────────────
    "Electrical Engineer": {
        "critical": ["Circuit Design", "PCB Layout (Altium/KiCad)", "Embedded C", "Power Electronics", "Signal Processing", "Oscilloscope/Multimeter"],
        "important": ["MATLAB/Simulink", "FPGA (VHDL/Verilog)", "PLC Programming", "EMC/EMI Design", "Battery Systems", "Python"],
        "emerging": ["EV Powertrain Design", "Wide-Bandgap Semiconductors (SiC/GaN)", "Digital Twins", "Edge AI Hardware"],
    },
    "Mechanical Engineer": {
        "critical": ["CAD (SolidWorks/CATIA)", "FEA (ANSYS/Abaqus)", "GD&T", "Thermodynamics", "Fluid Mechanics", "Manufacturing Processes"],
        "important": ["MATLAB", "CFD Simulation", "3D Printing/Additive Mfg", "Project Management", "Material Science", "Python"],
        "emerging": ["Generative Design (AI CAD)", "Digital Twins", "Topology Optimization", "Sustainable Engineering"],
    },
    "Civil Engineer": {
        "critical": ["AutoCAD/Civil 3D", "Structural Analysis", "Surveying", "Soil Mechanics", "Project Management", "Building Codes"],
        "important": ["STAAD.Pro/SAP2000", "GIS (ArcGIS)", "Concrete/Steel Design", "BIM (Revit)", "Environmental Regulations", "Cost Estimation"],
        "emerging": ["BIM + Digital Twin", "Smart Infrastructure", "Green Building (LEED)", "AI Structural Optimization"],
    },
    "Biomedical Engineer": {
        "critical": ["Biomechanics", "Medical Device Design (FDA 21 CFR Part 820)", "MATLAB", "Signal Processing (ECG/EEG)", "CAD", "Python"],
        "important": ["Regulatory Affairs (ISO 13485)", "Biocompatibility Testing", "Image Processing (MRI/CT)", "Statistics", "Clinical Trials basics"],
        "emerging": ["AI Diagnostics", "Organ-on-Chip", "Wearable Health Tech", "CRISPR Tools for Engineers"],
    },

    # ── Research / Academia ───────────────────────────────────────────────────
    "Research Scientist": {
        "critical": ["Python/R", "Statistical Analysis", "Scientific Writing", "Literature Review", "Experiment Design", "Data Visualization"],
        "important": ["Machine Learning", "SQL", "LaTeX", "Grant Writing", "Collaboration Tools", "Domain-specific Tools (e.g., Bioinformatics)"],
        "emerging": ["LLM-Assisted Research", "Open Science Tools", "Reproducible Research (Jupyter/Quarto)", "AI Co-authoring"],
    },

    # ── Education ────────────────────────────────────────────────────────────
    "Teacher / Educator": {
        "critical": ["Curriculum Design", "Classroom Management", "Differentiated Instruction", "Assessment Design", "Communication", "Subject Expertise"],
        "important": ["Google Classroom/Canvas LMS", "EdTech Tools (Kahoot, Nearpod)", "IEP/504 Compliance", "Data-Driven Instruction", "Parent Communication"],
        "emerging": ["AI-Powered Tutoring Tools", "Adaptive Learning Platforms", "Micro-credentialing", "Virtual Classroom Design"],
    },

    # ── Supply Chain ──────────────────────────────────────────────────────────
    "Supply Chain Analyst": {
        "critical": ["Excel (advanced)", "SQL", "ERP (SAP/Oracle)", "Demand Forecasting", "Inventory Management", "Data Analysis"],
        "important": ["Python/R", "Tableau/Power BI", "Logistics Optimization", "Supplier Management", "S&OP Process", "Six Sigma"],
        "emerging": ["AI/ML Forecasting", "Blockchain for Traceability", "Digital Supply Chain Twins", "Sustainable Sourcing"],
    },
}

ALL_ROLES = sorted(ROLE_SKILLS.keys())
