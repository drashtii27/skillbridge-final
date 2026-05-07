"""
SkillBridge AI – Skill Knowledge Base
Specific resources, projects, and learning paths for each skill.
Used by Model 3 (Projects) and Model 4 (Roadmap) when offline.
"""

# Real learning resources per skill (2025)
SKILL_RESOURCES = {
    # ── Programming Languages ──
    "Python": {"courses": ["CS50P (Harvard, free)", "Python for Everybody (Coursera)", "Automate the Boring Stuff"], "docs": "docs.python.org", "practice": "LeetCode Python track, HackerRank Python"},
    "Python (Pandas)": {"courses": ["Kaggle Pandas micro-course (free)", "Data Analysis with Python (freeCodeCamp)"], "docs": "pandas.pydata.org", "practice": "Kaggle datasets, StrataScratch"},
    "Java": {"courses": ["Java MOOC (Helsinki, free)", "Java Masterclass (Udemy)"], "docs": "dev.java", "practice": "LeetCode Java, CodingBat"},
    "JavaScript/TypeScript": {"courses": ["JavaScript.info (free)", "TypeScript Deep Dive (free)"], "docs": "developer.mozilla.org", "practice": "Exercism.io, Frontend Mentor"},
    "Go": {"courses": ["Go by Example (free)", "Go Tour (official)"], "docs": "go.dev/doc", "practice": "Exercism Go track"},
    "Rust": {"courses": ["The Rust Book (free)", "Rustlings exercises"], "docs": "doc.rust-lang.org", "practice": "Exercism Rust track"},
    "R": {"courses": ["R for Data Science (free book)", "DataCamp R intro"], "docs": "r-project.org", "practice": "Kaggle R notebooks"},
    "C++": {"courses": ["LearnCpp.com (free)", "C++ Primer book"], "docs": "cppreference.com", "practice": "LeetCode C++, Codeforces"},
    "Embedded C/C++": {"courses": ["Embedded Systems (Coursera, CU Boulder)", "Making Embedded Systems book"], "docs": "ARM documentation", "practice": "STM32 projects, Arduino"},

    # ── DSA ──
    "DSA (Trees, Graphs, DP, Binary Search)": {"courses": ["NeetCode 150 (free)", "Striver's A2Z DSA Sheet", "AlgoExpert"], "docs": "neetcode.io/roadmap", "practice": "LeetCode (Blind 75 → NeetCode 150 → NeetCode All)"},

    # ── SQL ──
    "SQL": {"courses": ["SQLBolt (free)", "Mode Analytics SQL Tutorial", "DataLemur SQL"], "docs": "postgresql.org/docs", "practice": "DataLemur, StrataScratch, LeetCode SQL 50"},
    "SQL (Joins, Indexing, CTEs)": {"courses": ["Advanced SQL (DataLemur)", "Window Functions tutorial (Mode)"], "docs": "postgresql.org/docs", "practice": "DataLemur, HackerRank SQL, StrataScratch"},
    "SQL (Window Functions, CTEs, Joins)": {"courses": ["DataLemur SQL tutorial", "Mode Analytics Advanced SQL"], "docs": "postgresql.org/docs", "practice": "DataLemur 50 questions, StrataScratch"},

    # ── Web Frameworks ──
    "React 19+": {"courses": ["React.dev official tutorial (free)", "Full Stack Open (Helsinki, free)"], "docs": "react.dev", "practice": "Build a Kanban board, Build a chat app"},
    "React/Next.js": {"courses": ["Next.js Learn (official, free)", "Full Stack Open"], "docs": "nextjs.org/docs", "practice": "Build a blog with MDX, SaaS dashboard"},
    "Next.js 14+": {"courses": ["Next.js Learn (official, free)", "Vercel tutorials"], "docs": "nextjs.org/docs", "practice": "Build a full-stack app with Server Actions"},
    "TypeScript": {"courses": ["TypeScript Handbook (free)", "Total TypeScript (Matt Pocock)"], "docs": "typescriptlang.org/docs", "practice": "Type Challenges repo on GitHub"},
    "Python (FastAPI/Django)": {"courses": ["FastAPI official tutorial (free)", "Django for Beginners book"], "docs": "fastapi.tiangolo.com", "practice": "Build REST API for a todo app, blog API"},
    "Java (Spring Boot)": {"courses": ["Spring Boot official guides (free)", "Amigoscode Spring Boot"], "docs": "spring.io/guides", "practice": "Build microservice with Spring Boot"},
    "Node.js": {"courses": ["The Odin Project (free)", "Node.js official docs"], "docs": "nodejs.org/docs", "practice": "Build Express API, real-time chat with Socket.io"},

    # ── Data / ML ──
    "Pandas/NumPy": {"courses": ["Kaggle Pandas course (free)", "NumPy official tutorial"], "docs": "pandas.pydata.org", "practice": "Kaggle competitions, EDA on real datasets"},
    "Scikit-learn": {"courses": ["Scikit-learn MOOC (free)", "Hands-on ML book (Aurélien Géron)"], "docs": "scikit-learn.org", "practice": "Kaggle Titanic, House Prices, classification tasks"},
    "PyTorch": {"courses": ["PyTorch official tutorials (free)", "Fast.ai course (free)"], "docs": "pytorch.org/tutorials", "practice": "Train MNIST, fine-tune BERT, image classifier"},
    "PyTorch/TensorFlow": {"courses": ["Fast.ai (free)", "Deep Learning Specialization (Coursera)"], "docs": "pytorch.org", "practice": "Kaggle image classification, NLP tasks"},
    "HuggingFace Transformers": {"courses": ["HuggingFace NLP Course (free)", "LLM University by Cohere (free)"], "docs": "huggingface.co/docs", "practice": "Fine-tune BERT for classification, build text pipeline"},
    "Statistics & Probability": {"courses": ["Khan Academy Statistics (free)", "StatQuest YouTube (free)"], "docs": "onlinestatbook.com", "practice": "AB testing simulations, hypothesis testing exercises"},
    "Statistics": {"courses": ["Khan Academy (free)", "Think Stats (free book)"], "docs": "statsmodels.org", "practice": "Kaggle analysis projects"},
    "ML Algorithms": {"courses": ["Andrew Ng ML Specialization (Coursera)", "StatQuest ML playlist"], "docs": "scikit-learn.org", "practice": "Kaggle competitions (Tabular Playground)"},
    "Feature Engineering": {"courses": ["Kaggle Feature Engineering course (free)", "Feature Engineering for ML book"], "docs": "scikit-learn preprocessing", "practice": "Kaggle feature engineering competitions"},
    "A/B Testing": {"courses": ["Udacity A/B Testing (free)", "Evan Miller's blog"], "docs": "statsmodels.org", "practice": "Build A/B test simulator in Python"},
    "Spark": {"courses": ["Databricks Academy (free)", "PySpark tutorial"], "docs": "spark.apache.org", "practice": "Process 1GB+ dataset with PySpark"},
    "Apache Spark": {"courses": ["Databricks Academy (free)", "Learning Spark book"], "docs": "spark.apache.org", "practice": "ETL pipeline on large CSV"},
    "Apache Airflow": {"courses": ["Airflow official tutorial (free)", "Astronomer Academy"], "docs": "airflow.apache.org", "practice": "Build DAG pipeline for data ingestion"},

    # ── DevOps / Cloud ──
    "Docker": {"courses": ["Docker Get Started (official, free)", "TechWorld with Nana YouTube"], "docs": "docs.docker.com", "practice": "Containerize a Python app, multi-stage builds"},
    "Kubernetes": {"courses": ["Kubernetes official tutorials (free)", "KodeKloud"], "docs": "kubernetes.io/docs", "practice": "Deploy app on Minikube, Helm charts"},
    "CI/CD": {"courses": ["GitHub Actions docs (free)", "GitLab CI tutorial"], "docs": "docs.github.com/actions", "practice": "Set up CI/CD for a real project"},
    "CI/CD (GitHub Actions)": {"courses": ["GitHub Actions official docs (free)", "DevOps with GitHub Actions"], "docs": "docs.github.com/actions", "practice": "Build test-lint-deploy pipeline"},
    "Terraform": {"courses": ["HashiCorp Learn (free)", "Terraform Up & Running book"], "docs": "developer.hashicorp.com", "practice": "Provision AWS infra with Terraform"},
    "AWS/GCP/Azure": {"courses": ["AWS Cloud Practitioner (free tier)", "GCP Digital Leader"], "docs": "aws.amazon.com/documentation", "practice": "Deploy app on EC2, set up S3, Lambda function"},
    "Linux/Bash": {"courses": ["Linux Journey (free)", "OverTheWire Bandit wargame"], "docs": "man7.org", "practice": "OverTheWire challenges, write Bash scripts"},
    "Git": {"courses": ["Git Immersion (free)", "Atlassian Git tutorials"], "docs": "git-scm.com/doc", "practice": "Contribute to open-source, branching workflows"},
    "REST APIs": {"courses": ["RESTful API design (freeCodeCamp)", "Postman Learning Center"], "docs": "restfulapi.net", "practice": "Build and document a REST API"},

    # ── Data Viz / BI ──
    "Tableau/Power BI": {"courses": ["Tableau Free Training Videos (official)", "Power BI Guided Learning (Microsoft)"], "docs": "help.tableau.com", "practice": "Build 3 dashboards on public datasets"},
    "Excel (Advanced)": {"courses": ["Excel Skills for Business (Coursera)", "Chandoo.org (free)"], "docs": "support.microsoft.com", "practice": "Build financial model, pivot tables, VLOOKUP/INDEX-MATCH"},
    "Google Analytics 4": {"courses": ["Google Analytics Academy (free)", "GA4 Skillshop certification"], "docs": "support.google.com/analytics", "practice": "Set up GA4 on a test site, build reports"},

    # ── Engineering ──
    "AutoCAD": {"courses": ["AutoCAD official tutorials (free)", "Coursera AutoCAD specialization"], "docs": "knowledge.autodesk.com", "practice": "Draft a building floor plan, site layout"},
    "Civil 3D": {"courses": ["Autodesk Civil 3D tutorials (free)", "InfraWorks + Civil 3D workflow"], "docs": "knowledge.autodesk.com", "practice": "Design a road alignment, grading plan"},
    "Structural Analysis (SAP2000/ETABS)": {"courses": ["CSI SAP2000 tutorials (YouTube)", "ETABS official webinars"], "docs": "wiki.csiamerica.com", "practice": "Analyze a 3-story frame, beam design"},
    "Revit (BIM)": {"courses": ["Autodesk Revit Learning (free)", "BIM Handbook"], "docs": "knowledge.autodesk.com", "practice": "Model a small building in Revit"},
    "SolidWorks/CATIA": {"courses": ["SolidWorks tutorials (official)", "MySolidWorks (free)"], "docs": "help.solidworks.com", "practice": "Design an assembly, run FEA simulation"},
    "ANSYS (FEA/CFD)": {"courses": ["ANSYS Innovation Courses (free)", "SimCafe Cornell tutorials"], "docs": "ansyshelp.ansys.com", "practice": "Stress analysis on bracket, thermal simulation"},
    "MATLAB": {"courses": ["MATLAB Onramp (MathWorks, free)", "MIT OCW signals and systems"], "docs": "mathworks.com/help", "practice": "Signal processing project, control system simulation"},

    # ── Healthcare ──
    "EHR (Epic/Cerner)": {"courses": ["Epic UserWeb training", "Cerner Learning Portal"], "docs": "Epic UserWeb", "practice": "Complete EHR certification modules"},
    "Patient Assessment": {"courses": ["Khan Academy Health & Medicine (free)", "Clinical Skills videos"], "docs": "Nursing textbooks (Jarvis Physical Examination)", "practice": "Simulation labs, case studies"},
    "BLS/ACLS": {"courses": ["AHA BLS/ACLS courses", "Red Cross certification"], "docs": "heart.org", "practice": "Complete certification, practice simulations"},

    # ── Business ──
    "Requirements (BRD/FRD)": {"courses": ["BA Essentials (Udemy)", "IIBA BABOK Guide"], "docs": "iiba.org", "practice": "Write BRD for a sample app, create use case diagrams"},
    "BPMN": {"courses": ["BPMN 2.0 Tutorial (Camunda, free)", "Signavio Academic"], "docs": "bpmn.org", "practice": "Model 3 business processes in Camunda Modeler"},
    "Jira/Confluence": {"courses": ["Atlassian University (free)", "Jira Fundamentals badge"], "docs": "support.atlassian.com", "practice": "Set up a Scrum board, create sprint backlog"},
    "Figma": {"courses": ["Figma official tutorials (free)", "Figma UI Design (YouTube)"], "docs": "help.figma.com", "practice": "Design a mobile app UI, create a design system"},
    "Product Strategy & Roadmapping": {"courses": ["Product School (free YouTube)", "Reforge (paid)"], "docs": "svpg.com/articles", "practice": "Create a product roadmap for a sample startup"},

    # ── Emerging 2025 ──
    "LLM Integration": {"courses": ["LangChain docs (free)", "DeepLearning.AI short courses (free)"], "docs": "langchain.com/docs", "practice": "Build a RAG chatbot, integrate OpenAI API"},
    "RAG Architecture": {"courses": ["LlamaIndex docs (free)", "DeepLearning.AI RAG course"], "docs": "docs.llamaindex.ai", "practice": "Build RAG system with ChromaDB + LlamaIndex"},
    "LoRA/PEFT Fine-tuning": {"courses": ["HuggingFace PEFT docs (free)", "DeepLearning.AI fine-tuning course"], "docs": "huggingface.co/docs/peft", "practice": "Fine-tune Llama-2 with LoRA on custom data"},
    "MLOps": {"courses": ["Made With ML (free)", "MLOps Zoomcamp (free)"], "docs": "ml-ops.org", "practice": "Deploy model with MLflow, build CI/CD for ML"},
    "AI-assisted Coding": {"courses": ["GitHub Copilot docs", "Cursor IDE tutorial"], "docs": "docs.github.com/copilot", "practice": "Use Copilot/Cursor for a full project"},
    "Telehealth Nursing": {"courses": ["ANA Telehealth resources", "Coursera Telehealth specialization"], "docs": "telehealth.hhs.gov", "practice": "Complete telehealth certification modules"},
    "AI Structural Design": {"courses": ["Generative Design in Fusion 360", "AI in AEC webinars"], "docs": "autodesk.com/generative-design", "practice": "Use topology optimization in Fusion 360"},
    "Digital Twins": {"courses": ["Azure Digital Twins docs (free)", "Siemens learning"], "docs": "learn.microsoft.com/azure/digital-twins", "practice": "Create a simple digital twin model"},
}

# Specific project ideas per skill
SKILL_PROJECTS = {
    "Python": {"title": "CLI Task Automation Tool", "desc": "Build a Python CLI that automates file organization, web scraping, and report generation. Uses argparse, pathlib, requests.", "stack": ["Python 3.12+", "Click/Typer", "Rich", "Requests"], "time": "1 week"},
    "Python (Pandas)": {"title": "COVID/Stock Market Data Dashboard", "desc": "Analyze real-world dataset (COVID stats, stock prices, or sports data) with Pandas. Create visualizations and statistical insights.", "stack": ["Pandas", "Matplotlib", "Seaborn", "Jupyter"], "time": "1 week"},
    "SQL (Window Functions, CTEs, Joins)": {"title": "E-commerce Analytics SQL Project", "desc": "Write 20+ complex SQL queries analyzing customer behavior, revenue trends, cohort analysis using CTEs and window functions on a sample e-commerce database.", "stack": ["PostgreSQL", "DBeaver", "Sample DB (Northwind/Sakila)"], "time": "5 days"},
    "SQL (Joins, Indexing, CTEs)": {"title": "Database Performance Optimization Report", "desc": "Take a slow database, write optimized queries with proper indexes, CTEs, and joins. Document before/after query plans.", "stack": ["PostgreSQL", "EXPLAIN ANALYZE", "Indexing strategies"], "time": "5 days"},
    "DSA (Trees, Graphs, DP, Binary Search)": {"title": "LeetCode Solutions Repository", "desc": "Solve 100+ LeetCode problems (Blind 75 + NeetCode 150). Document approach, time/space complexity for each. Organize by pattern.", "stack": ["Python/Java", "Git", "Markdown"], "time": "4-6 weeks ongoing"},
    "React 19+": {"title": "Real-time Collaboration App", "desc": "Build a Notion-like editor with real-time collaboration using React 19 Server Components, WebSocket, and optimistic UI updates.", "stack": ["React 19", "Next.js 14", "Tailwind CSS", "Socket.io"], "time": "2 weeks"},
    "Docker": {"title": "Multi-Container DevOps Pipeline", "desc": "Containerize a full-stack app (frontend + API + database) with Docker Compose. Add health checks, volumes, and CI/CD.", "stack": ["Docker", "Docker Compose", "GitHub Actions", "Nginx"], "time": "1 week"},
    "Kubernetes": {"title": "K8s Microservice Deployment", "desc": "Deploy a 3-service app on Kubernetes with Helm charts, auto-scaling, and monitoring.", "stack": ["Kubernetes", "Helm", "Prometheus", "Minikube"], "time": "2 weeks"},
    "Tableau/Power BI": {"title": "Interactive Business Intelligence Dashboard", "desc": "Build a multi-page dashboard analyzing sales data with drill-downs, filters, KPIs, and trend analysis.", "stack": ["Tableau Public / Power BI Desktop", "Sample dataset"], "time": "1 week"},
    "Excel (Advanced)": {"title": "Financial Model & Forecasting Spreadsheet", "desc": "Build a 3-statement financial model with DCF valuation, scenario analysis, pivot tables, and VBA macros.", "stack": ["Excel", "VBA", "Pivot Tables", "Data Validation"], "time": "1 week"},
    "AutoCAD": {"title": "Residential Building Design Package", "desc": "Create complete construction drawings including floor plans, elevations, sections, and site plan for a small residential building.", "stack": ["AutoCAD 2025", "Layer management", "Plotting"], "time": "2 weeks"},
    "Revit (BIM)": {"title": "BIM Model of Commercial Building", "desc": "Create a full BIM model including architectural, structural, and MEP systems. Generate schedules and clash detection reports.", "stack": ["Revit 2025", "Navisworks", "BIM 360"], "time": "3 weeks"},
    "SolidWorks/CATIA": {"title": "Product Design & FEA Analysis", "desc": "Design a consumer product (phone stand, drone frame) with full assembly, engineering drawings, and FEA stress analysis.", "stack": ["SolidWorks 2025", "FEA Simulation", "Assembly"], "time": "2 weeks"},
    "Requirements (BRD/FRD)": {"title": "Complete BRD for Mobile Banking App", "desc": "Write a professional BRD including business objectives, scope, functional requirements, use cases, wireframes, and acceptance criteria.", "stack": ["Google Docs/Confluence", "Lucidchart", "Figma wireframes"], "time": "1 week"},
    "BPMN": {"title": "Process Improvement Case Study", "desc": "Map current-state (AS-IS) and future-state (TO-BE) processes for a real business scenario using BPMN 2.0. Calculate efficiency gains.", "stack": ["Camunda Modeler (free)", "BPMN 2.0", "Process metrics"], "time": "1 week"},
    "Figma": {"title": "Complete Mobile App UI/UX Design", "desc": "Design a full mobile app (10+ screens) with design system, components, auto-layout, prototyping, and user flow.", "stack": ["Figma", "Auto Layout", "Components", "Prototype"], "time": "1-2 weeks"},
    "Scikit-learn": {"title": "End-to-End ML Classification Pipeline", "desc": "Build a complete ML pipeline: data cleaning, EDA, feature engineering, model selection (5+ algorithms compared), hyperparameter tuning, and deployment.", "stack": ["Scikit-learn", "Pandas", "Matplotlib", "Streamlit"], "time": "2 weeks"},
    "PyTorch": {"title": "Custom Image Classifier with Transfer Learning", "desc": "Fine-tune a pre-trained model (ResNet/EfficientNet) on custom dataset. Build inference API and web demo.", "stack": ["PyTorch", "torchvision", "FastAPI", "Gradio"], "time": "2 weeks"},
    "Git": {"title": "Open Source Contribution Portfolio", "desc": "Contribute to 3+ open-source projects. Document PRs, code reviews, and branching strategies used.", "stack": ["Git", "GitHub", "Markdown"], "time": "Ongoing"},
    "System Design": {"title": "System Design Portfolio", "desc": "Design 5 systems (URL shortener, chat app, Twitter clone, payment system, video streaming) with architecture diagrams, trade-offs, and capacity estimates.", "stack": ["Draw.io/Excalidraw", "Markdown", "GitHub"], "time": "3 weeks"},
    "REST APIs": {"title": "Production-Ready REST API", "desc": "Build a fully documented REST API with authentication, pagination, rate limiting, error handling, and automated tests.", "stack": ["FastAPI/Express", "PostgreSQL", "Swagger/OpenAPI", "pytest"], "time": "2 weeks"},
    "Terraform": {"title": "Infrastructure as Code Portfolio", "desc": "Provision complete cloud infrastructure (VPC, EC2, RDS, S3, Lambda) using Terraform modules with state management.", "stack": ["Terraform", "AWS Free Tier", "GitHub Actions"], "time": "2 weeks"},
    "Statistics & Probability": {"title": "Statistical Analysis Research Report", "desc": "Conduct a full statistical analysis on a real dataset: hypothesis testing, confidence intervals, regression, and ANOVA with visualizations.", "stack": ["Python/R", "scipy.stats", "matplotlib", "Jupyter"], "time": "1 week"},
    "Google Analytics 4": {"title": "GA4 Analytics & Reporting Setup", "desc": "Set up GA4 on a demo site, configure events, conversions, audiences, and build a custom Looker Studio dashboard.", "stack": ["GA4", "Google Tag Manager", "Looker Studio"], "time": "1 week"},
    "Product Strategy & Roadmapping": {"title": "Product Strategy Document for AI Startup", "desc": "Create a comprehensive product strategy: market research, competitive analysis, user personas, feature prioritization (RICE), and 12-month roadmap.", "stack": ["Notion/Confluence", "Miro", "Figma"], "time": "2 weeks"},
}

def get_resource(skill):
    """Get learning resource for a skill, with fuzzy matching."""
    if skill in SKILL_RESOURCES:
        return SKILL_RESOURCES[skill]
    # Fuzzy match
    skill_lower = skill.lower()
    for k, v in SKILL_RESOURCES.items():
        if skill_lower in k.lower() or k.lower() in skill_lower:
            return v
    return {"courses": [f"Search '{skill} tutorial 2025' on YouTube/Coursera"], "docs": f"Official {skill} documentation", "practice": f"Build a project using {skill}"}

def get_project(skill, role=""):
    """Get specific project idea for a skill."""
    if skill in SKILL_PROJECTS:
        return SKILL_PROJECTS[skill]
    skill_lower = skill.lower()
    for k, v in SKILL_PROJECTS.items():
        if skill_lower in k.lower() or k.lower() in skill_lower:
            return v
    return {"title": f"{role} {skill} Portfolio Project", "desc": f"Build a real-world project demonstrating {skill} for {role} role.", "stack": [skill, "Git", "Documentation"], "time": "1-2 weeks"}
