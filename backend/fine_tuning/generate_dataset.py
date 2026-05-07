"""
Generate Alpaca-format JSONL dataset for fine-tuning Nemotron.
Run: python -m backend.fine_tuning.generate_dataset
"""

import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from backend.core.config import ROLE_SKILLS

ROADMAP_INSTRUCTION = "Generate a detailed week-by-week learning roadmap for acquiring the specified skill within the given timeframe."
INTERVIEW_INSTRUCTION = "Generate 5 realistic technical interview questions with answer outlines for the given role and skill."
SKILL_EXTRACT_INSTRUCTION = "Extract all technical skills from the following resume text. Return as a comma-separated list."

SAMPLE_RESUMES = [
    "Software Engineer with 3 years experience. Skills: Python, Django, PostgreSQL, Docker, Git, REST APIs, unit testing.",
    "Data Scientist. Proficient in R, Python, pandas, scikit-learn, Tableau, SQL, hypothesis testing, regression analysis.",
    "Frontend Developer. Expert in React, TypeScript, Next.js, Tailwind CSS, GraphQL, Jest, Cypress, Webpack.",
    "DevOps Engineer. Experience with AWS EC2/S3/RDS, Terraform, Kubernetes, Helm, CI/CD, Prometheus, Bash scripting.",
    "ML Engineer. PyTorch, TensorFlow, Hugging Face, MLflow, FastAPI, Docker, Kubernetes, CUDA, Python, NumPy.",
]

SAMPLE_ROADMAPS = {
    "PyTorch": """Week 1: Tensors, autograd, basic operations
Resources: PyTorch official tutorials (free), freeCodeCamp YouTube 5h course
Project: MNIST digit classifier from scratch

Week 2: Neural networks, nn.Module, loss functions, optimizers
Resources: fast.ai Part 1 (free), StatQuest YouTube
Project: Binary image classifier

Week 3: CNNs, transfer learning with torchvision
Resources: PyTorch docs, Papers With Code examples
Project: Fine-tune ResNet on custom dataset

Week 4: RNNs, attention, transformer basics
Resources: Andrej Karpathy YouTube, The Annotated Transformer
Project: Text sentiment classifier""",

    "React": """Week 1: JSX, components, props, state with useState
Resources: React official docs (react.dev), Scrimba React (free)
Project: Todo app with CRUD operations

Week 2: useEffect, context, custom hooks
Resources: Dave Gray YouTube React course, Epic React by Kent C. Dodds
Project: Weather app with API integration

Week 3: React Router, code splitting, performance optimization
Resources: React Router docs, Next.js official docs
Project: Multi-page portfolio site

Week 4: Testing with Vitest/React Testing Library, deployment
Resources: Testing Library docs, Vercel deployment guide
Project: Full tested portfolio deployed on Vercel""",
}


def make_roadmap_sample(skill: str, weeks: int = 4) -> dict:
    roadmap = SAMPLE_ROADMAPS.get(skill, f"""Week 1-{weeks}: Learn {skill} fundamentals
Resources: Official documentation, YouTube tutorials, Coursera free audit
Project: Build a working project demonstrating core {skill} concepts
Checkpoint: Can explain and implement key {skill} patterns from memory""")

    return {
        "instruction": ROADMAP_INSTRUCTION,
        "input": f"Skill: {skill}\nTimeframe: {weeks} weeks\nCurrent level: Beginner",
        "output": roadmap,
    }


def make_interview_sample(role: str, skill: str) -> dict:
    questions = []
    base_questions = {
        "Python": [
            "Explain the difference between a list and a tuple in Python. When would you use each?",
            "What are Python decorators and how do they work? Provide a practical example.",
            "Describe the GIL (Global Interpreter Lock) and its implications for multithreading.",
        ],
        "Machine Learning": [
            "Explain the bias-variance tradeoff and how it affects model selection.",
            "When would you use L1 vs L2 regularization?",
            "Describe the process of feature selection and which methods you prefer.",
        ],
    }
    qs = base_questions.get(skill, [f"Explain a key concept in {skill} and its practical application."])
    for q in qs[:2]:
        questions.append({"question": q, "difficulty": random.choice(["Easy", "Medium", "Hard"]),
                          "skills_tested": [skill], "answer_outline": [f"Demonstrate knowledge of {skill}"]})

    return {
        "instruction": INTERVIEW_INSTRUCTION,
        "input": f"Role: {role}\nSkill: {skill}",
        "output": json.dumps(questions),
    }


def make_skill_extract_sample(resume_text: str, expected_skills: list) -> dict:
    return {
        "instruction": SKILL_EXTRACT_INSTRUCTION,
        "input": resume_text,
        "output": ", ".join(expected_skills),
    }


def generate_dataset(output_path: str = "data/finetune_dataset.jsonl", n_samples: int = 2000):
    Path("data").mkdir(exist_ok=True)
    samples = []

    roles = list(ROLE_SKILLS.keys())

    for _ in range(n_samples // 3):
        role = random.choice(roles)
        all_skills = (
            ROLE_SKILLS[role].get("critical", [])[:3]
            + ROLE_SKILLS[role].get("important", [])[:2]
        )
        for skill in random.sample(all_skills, min(2, len(all_skills))):
            samples.append(make_roadmap_sample(skill, random.choice([2, 3, 4, 6])))
            samples.append(make_interview_sample(role, skill))

    for resume in SAMPLE_RESUMES:
        words = resume.lower().replace(",", " ").split()
        tech_words = [w for w in words if len(w) > 3 and w[0].isupper() or w in ["python", "react", "sql", "docker", "git", "aws"]]
        samples.append(make_skill_extract_sample(resume, tech_words[:8]))

    random.shuffle(samples)
    samples = samples[:n_samples]

    with open(output_path, "w") as f:
        for s in samples:
            f.write(json.dumps(s) + "\n")

    print(f"Generated {len(samples)} samples → {output_path}")
    return output_path


if __name__ == "__main__":
    path = generate_dataset()
    print(f"Dataset ready: {path}")
