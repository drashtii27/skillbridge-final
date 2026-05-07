"""ChromaDB-backed RAG pipeline for grounding LLM responses."""

import chromadb
from chromadb.utils import embedding_functions
from loguru import logger
from ..core.config import get_settings, ROLE_SKILLS

_client = None
_skill_col = None
_jobs_col = None
_questions_col = None

SEED_RESOURCES = {
    "Python": "Python Docs: https://docs.python.org | Corey Schafer YouTube | Real Python | CS50P Harvard (free)",
    "PyTorch": "PyTorch Tutorials: https://pytorch.org/tutorials | freeCodeCamp YouTube 5h | fast.ai course (free) | Papers With Code",
    "TensorFlow": "TensorFlow Docs | DeepLearning.AI TF cert | YouTube: TensorFlow 2.0 Full Course | Kaggle Learn",
    "React": "React Docs (react.dev) | Scrimba React Bootcamp | Traversy Media YouTube | Epic React by Kent C. Dodds",
    "Next.js": "Next.js Docs | Fireship YouTube | Lee Robinson channel | Vercel tutorials",
    "Docker": "Docker Docs | TechWorld with Nana YouTube | KodeKloud free labs | Play with Docker",
    "Kubernetes": "Kubernetes Docs | TechWorld with Nana K8s course | CNCF free courses | KodeKloud",
    "SQL": "Mode Analytics SQL Tutorial (free) | SQLZoo | PostgreSQL Tutorial | CS186 UC Berkeley (YouTube)",
    "scikit-learn": "scikit-learn Docs | Kaggle Intro to ML | Hands-On ML book (Aurélien Géron) | StatQuest YouTube",
    "Machine Learning": "fast.ai (free) | Andrew Ng Coursera ML | Kaggle Learn | 3Blue1Brown Neural Networks YouTube",
    "LangChain": "LangChain Docs | Sam Witteveen YouTube | LangChain Python Cookbook | Greg Kamradt YouTube",
    "TypeScript": "TypeScript Docs | Matt Pocock Total TypeScript | Traversy Media | Execute Program",
    "AWS": "AWS Free Tier | A Cloud Guru | freeCodeCamp AWS YouTube | Adrian Cantrill courses",
    "Terraform": "HashiCorp Learn (free) | TechWorld with Nana | FreeCodeCamp Terraform | CloudSkills.io",
    "Data Structures": "NeetCode.io | LeetCode | MIT 6.006 (YouTube, free) | Grokking Algorithms book",
    "System Design": "System Design Primer (GitHub) | Grokking System Design | YouTube: TechDummies | ByteByteGo",
    "GraphQL": "GraphQL Docs | Odyssey by Apollo (free) | Fireship YouTube | How To GraphQL",
    "RAG": "LlamaIndex Docs | LangChain RAG Tutorial | DeepLearning.AI short courses | Hugging Face RLHF Course",
    "MLflow": "MLflow Docs | Databricks tutorials | YouTube: DSwithBappy | Full Stack Deep Learning",
    "Figma": "Figma Learn (official) | DesignCourse YouTube | Traversy Media Figma | Figma Community files",
}

DISCORD_SERVERS = {
    "Machine Learning Engineer": [
        {"name": "Hugging Face", "url": "https://discord.gg/huggingface", "members": "120k+"},
        {"name": "EleutherAI", "url": "https://discord.gg/zBGx3azzUn", "members": "20k+"},
        {"name": "Fast.ai Community", "url": "https://discord.gg/TA9KcFQXcJ", "members": "15k+"},
    ],
    "Data Scientist": [
        {"name": "DataTalks.Club", "url": "https://discord.gg/datatalks", "members": "50k+"},
        {"name": "Kaggle", "url": "https://discord.gg/kaggle", "members": "30k+"},
    ],
    "Software Engineer (Frontend)": [
        {"name": "Reactiflux", "url": "https://discord.gg/reactiflux", "members": "200k+"},
        {"name": "Tailwind CSS", "url": "https://discord.gg/tailwind", "members": "25k+"},
        {"name": "Next.js", "url": "https://discord.gg/nextjs", "members": "40k+"},
    ],
    "Software Engineer (Backend)": [
        {"name": "Programmers Hangout", "url": "https://discord.gg/programming", "members": "300k+"},
        {"name": "Python Discord", "url": "https://discord.gg/python", "members": "250k+"},
        {"name": "Go Community", "url": "https://discord.gg/golang", "members": "30k+"},
    ],
    "DevOps / Cloud Engineer": [
        {"name": "DevOps Lounge", "url": "https://discord.gg/devops", "members": "40k+"},
        {"name": "Kubernetes", "url": "https://discord.gg/kubernetes", "members": "60k+"},
    ],
    "default": [
        {"name": "The Coding Den", "url": "https://discord.gg/code", "members": "100k+"},
        {"name": "CS Career Hub", "url": "https://discord.gg/cscareerhub", "members": "80k+"},
        {"name": "Programmer's Hangout", "url": "https://discord.gg/programming", "members": "300k+"},
    ],
}

COLLAB_PLATFORMS = [
    {"name": "GitHub Codespaces", "url": "https://github.com/codespaces", "desc": "Full VS Code in browser, share link"},
    {"name": "Replit", "url": "https://replit.com", "desc": "Multiplayer coding, instant start"},
    {"name": "CodeSandbox", "url": "https://codesandbox.io", "desc": "Web dev environments, live collaboration"},
    {"name": "Excalidraw", "url": "https://excalidraw.com", "desc": "Collaborative whiteboard for system design"},
    {"name": "LiveShare (VS Code)", "url": "https://marketplace.visualstudio.com/items?itemName=MS-vsliveshare.vsliveshare", "desc": "Real-time pair programming"},
]


def get_client():
    global _client, _skill_col, _jobs_col, _questions_col
    if _client is None:
        settings = get_settings()
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        ef = embedding_functions.DefaultEmbeddingFunction()
        _skill_col = _client.get_or_create_collection("skill_resources", embedding_function=ef)
        _jobs_col = _client.get_or_create_collection("job_descriptions", embedding_function=ef)
        _questions_col = _client.get_or_create_collection("interview_questions", embedding_function=ef)
        _seed_skills()
    return _client, _skill_col, _jobs_col, _questions_col


def _seed_skills():
    global _skill_col
    if _skill_col.count() > 0:
        return
    docs, ids, metas = [], [], []
    for skill, resources in SEED_RESOURCES.items():
        docs.append(f"Skill: {skill}\nResources: {resources}")
        ids.append(f"skill_{skill.lower().replace(' ', '_')}")
        metas.append({"skill": skill})
    # Also seed from ROLE_SKILLS
    for role, data in ROLE_SKILLS.items():
        all_skills = data.get("critical", []) + data.get("important", []) + data.get("emerging", [])
        doc = f"Role: {role}\nRequired skills: {', '.join(all_skills)}"
        docs.append(doc)
        ids.append(f"role_{role.lower().replace(' ', '_').replace('/', '_')}")
        metas.append({"role": role})
    try:
        _skill_col.upsert(documents=docs, ids=ids, metadatas=metas)
        logger.info(f"Seeded {len(docs)} documents into ChromaDB skill_resources")
    except Exception as e:
        logger.warning(f"ChromaDB seed warning: {e}")


def retrieve_skill_context(skills: list[str], role: str, n_results: int = 5) -> str:
    try:
        _, skill_col, _, _ = get_client()
        query = f"{role}: {', '.join(skills[:8])}"
        results = skill_col.query(query_texts=[query], n_results=min(n_results, skill_col.count()))
        docs = results.get("documents", [[]])[0]
        return "\n---\n".join(docs)
    except Exception as e:
        logger.warning(f"RAG retrieval failed: {e}")
        return ""


def retrieve_similar_questions(role: str, skills: list[str], n_results: int = 5) -> str:
    try:
        _, _, _, q_col = get_client()
        if q_col.count() == 0:
            return ""
        query = f"Interview questions for {role} covering {', '.join(skills[:5])}"
        results = q_col.query(query_texts=[query], n_results=min(n_results, q_col.count()))
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs)
    except Exception as e:
        logger.warning(f"Questions RAG failed: {e}")
        return ""


def add_job_to_rag(job_id: str, title: str, company: str, description: str, role: str):
    try:
        _, _, jobs_col, _ = get_client()
        jobs_col.upsert(
            documents=[f"Job: {title} at {company}\nRole: {role}\n{description[:1000]}"],
            ids=[f"job_{job_id}"],
            metadatas=[{"role": role, "company": company}],
        )
    except Exception as e:
        logger.warning(f"Failed to add job to RAG: {e}")


def get_discord_servers(role: str) -> list[dict]:
    return DISCORD_SERVERS.get(role, DISCORD_SERVERS["default"])


def get_collab_platforms() -> list[dict]:
    return COLLAB_PLATFORMS


def get_skill_resources(skill: str) -> str:
    return SEED_RESOURCES.get(skill, f"Search for '{skill}' on YouTube, Coursera, or official documentation.")
