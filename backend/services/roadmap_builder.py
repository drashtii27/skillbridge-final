"""Builds structured RoadmapJSON using RAG + Nemotron."""

import json
from datetime import datetime, timezone
from loguru import logger
from .llm import call_nemotron, extract_json, ROADMAP_SYSTEM
from .rag import (
    retrieve_skill_context, get_discord_servers,
    get_collab_platforms, get_skill_resources,
)

YOUTUBE_RESOURCES = {
    "Python": [
        {"title": "Python Full Course – freeCodeCamp", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw", "channel": "freeCodeCamp"},
        {"title": "Python Tutorial – Corey Schafer", "url": "https://www.youtube.com/watch?v=YYXdXT2l-Gg", "channel": "Corey Schafer"},
    ],
    "PyTorch": [
        {"title": "PyTorch Full Course – freeCodeCamp", "url": "https://www.youtube.com/watch?v=Z_ikDlimN6A", "channel": "freeCodeCamp"},
        {"title": "PyTorch for Deep Learning – Daniel Bourke", "url": "https://www.youtube.com/watch?v=V_xro1bcAuA", "channel": "mrdbourke"},
    ],
    "React": [
        {"title": "React JS Full Course 2024 – Dave Gray", "url": "https://www.youtube.com/watch?v=RVFAyFWO4go", "channel": "Dave Gray"},
        {"title": "React Crash Course – Traversy Media", "url": "https://www.youtube.com/watch?v=w7ejDZ8SWv8", "channel": "Traversy Media"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Full Course – StatQuest", "url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI", "channel": "StatQuest"},
        {"title": "ML Zero to Hero – Google Brain", "url": "https://www.youtube.com/watch?v=VwVg9jCtqaU", "channel": "TensorFlow"},
    ],
    "Docker": [
        {"title": "Docker Tutorial for Beginners – TechWorld", "url": "https://www.youtube.com/watch?v=3c-iBn73dDE", "channel": "TechWorld with Nana"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Tutorial – TechWorld with Nana", "url": "https://www.youtube.com/watch?v=X48VuDVv0do", "channel": "TechWorld with Nana"},
    ],
    "System Design": [
        {"title": "System Design for Beginners – NeetCode", "url": "https://www.youtube.com/watch?v=i53Gi_K3o7I", "channel": "NeetCode"},
        {"title": "System Design Interview – ByteByteGo", "url": "https://www.youtube.com/watch?v=bUHFg8CZFws", "channel": "ByteByteGo"},
    ],
    "SQL": [
        {"title": "SQL Full Course – freeCodeCamp", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY", "channel": "freeCodeCamp"},
    ],
    "TypeScript": [
        {"title": "TypeScript Tutorial – Fireship", "url": "https://www.youtube.com/watch?v=ahCwqrYpIuM", "channel": "Fireship"},
    ],
    "Next.js": [
        {"title": "Next.js 14 Full Course – Dave Gray", "url": "https://www.youtube.com/watch?v=wm5gMKuwSYk", "channel": "Dave Gray"},
    ],
    "Data Structures": [
        {"title": "Data Structures Full Course – NeetCode", "url": "https://www.youtube.com/watch?v=pkYVOmU3MgA", "channel": "NeetCode"},
        {"title": "MIT 6.006 Intro to Algorithms", "url": "https://www.youtube.com/watch?v=ZA-tUyM_y7s", "channel": "MIT OpenCourseWare"},
    ],
    "LangChain": [
        {"title": "LangChain Crash Course – Greg Kamradt", "url": "https://www.youtube.com/watch?v=LbT1yp6quS8", "channel": "Greg Kamradt"},
    ],
}

COURSES = {
    "Python": [
        {"title": "CS50P – Python (Harvard)", "url": "https://cs50.harvard.edu/python/2022/", "platform": "edX", "free": True},
        {"title": "Python Bootcamp", "url": "https://www.udemy.com/course/complete-python-bootcamp/", "platform": "Udemy", "free": False},
    ],
    "Machine Learning": [
        {"title": "Machine Learning Specialization", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "platform": "Coursera", "free": True},
        {"title": "fast.ai Practical DL", "url": "https://course.fast.ai/", "platform": "fast.ai", "free": True},
    ],
    "React": [
        {"title": "Scrimba React Bootcamp", "url": "https://scrimba.com/learn/learnreact", "platform": "Scrimba", "free": True},
    ],
    "Docker": [
        {"title": "Play with Docker", "url": "https://training.play-with-docker.com/", "platform": "Docker", "free": True},
    ],
    "System Design": [
        {"title": "Grokking System Design", "url": "https://www.educative.io/courses/grokking-the-system-design-interview", "platform": "Educative", "free": False},
        {"title": "System Design Primer", "url": "https://github.com/donnemartin/system-design-primer", "platform": "GitHub", "free": True},
    ],
}

PRACTICE_PLATFORMS = {
    "coding": [
        {"name": "LeetCode", "url": "https://leetcode.com", "focus": "Algorithms & DS"},
        {"name": "NeetCode.io", "url": "https://neetcode.io", "focus": "Curated LeetCode problems"},
        {"name": "HackerRank", "url": "https://hackerrank.com", "focus": "Coding challenges"},
        {"name": "Codewars", "url": "https://codewars.com", "focus": "Kata-style challenges"},
    ],
    "projects": [
        {"name": "GitHub", "url": "https://github.com", "focus": "Host portfolio projects"},
        {"name": "Kaggle", "url": "https://kaggle.com", "focus": "ML competitions & datasets"},
        {"name": "Frontend Mentor", "url": "https://frontendmentor.io", "focus": "Frontend challenges"},
    ],
    "interviews": [
        {"name": "Pramp", "url": "https://pramp.com", "focus": "Mock interviews (free)"},
        {"name": "InterviewBit", "url": "https://interviewbit.com", "focus": "Structured interview prep"},
        {"name": "Interviewing.io", "url": "https://interviewing.io", "focus": "Anonymous mock interviews"},
    ],
}


def _get_youtube_for_skill(skill: str) -> list[dict]:
    for key, videos in YOUTUBE_RESOURCES.items():
        if key.lower() in skill.lower() or skill.lower() in key.lower():
            return videos[:2]
    return [{"title": f"Learn {skill} – YouTube Search", "url": f"https://www.youtube.com/results?search_query=learn+{skill.replace(' ', '+')}", "channel": "Various"}]


def _get_courses_for_skill(skill: str) -> list[dict]:
    for key, courses in COURSES.items():
        if key.lower() in skill.lower() or skill.lower() in key.lower():
            return courses[:2]
    return [{"title": f"{skill} Course", "url": f"https://coursera.org/search?query={skill.replace(' ', '+')}", "platform": "Coursera", "free": False}]


def _build_phase(month: int, skills_slice: list[str], total_months: int) -> dict:
    phase_titles = {1: "Foundation & Critical Skills", 2: "Core Proficiency", 3: "Advanced & Emerging Skills"}
    title = phase_titles.get(month, f"Month {month}: Deep Mastery")
    weeks = []
    for week_num, skill in enumerate(skills_slice[:4], start=1):
        position_pct = round(((month - 1) * 4 + week_num) / (total_months * 4) * 100, 1)
        week = {
            "week": week_num,
            "month": month,
            "skills_focus": [skill],
            "daily_plan": "1h theory → 1.5h hands-on coding → 30min review & notes",
            "resources": [
                *[{**v, "type": "youtube"} for v in _get_youtube_for_skill(skill)],
                *[{**c, "type": "course"} for c in _get_courses_for_skill(skill)],
                {"type": "docs", "title": f"{skill} Official Documentation", "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+official+docs", "free": True},
            ],
            "project": {
                "title": f"{skill} Mini Project",
                "description": f"Build a small project demonstrating your {skill} skills. Keep it in 1-3 days, focus on quality over quantity.",
                "tech_stack": [skill],
                "time_estimate": "2-3 days",
            },
            "checkpoint": f"Can you explain {skill} concepts and implement a working example from scratch?",
            "practice_platforms": PRACTICE_PLATFORMS["coding"][:2],
            "car_position_pct": position_pct,
        }
        weeks.append(week)
    return {"month": month, "title": title, "weeks": weeks}


async def generate_roadmap(
    role: str,
    user_skills: list[str],
    missing_skills: list[str],
    readiness_pct: float,
    months: int = 3,
) -> dict:
    rag_context = retrieve_skill_context(missing_skills[:8], role)
    discord_servers = get_discord_servers(role)
    collab_platforms = get_collab_platforms()

    # Distribute missing skills across phases
    critical_missing = missing_skills[:min(8, len(missing_skills))]
    skills_per_month = max(1, len(critical_missing) // months)

    phases = []
    for m in range(1, months + 1):
        start = (m - 1) * skills_per_month
        end = start + skills_per_month if m < months else len(critical_missing)
        month_skills = critical_missing[start:end]
        if month_skills:
            phases.append(_build_phase(m, month_skills, months))

    # LLM enhancement: generate portfolio projects & milestones
    llm_prompt = f"""Role: {role}
User has: {', '.join(user_skills[:10])}
Needs to learn: {', '.join(missing_skills[:8])}
Months: {months}
Context: {rag_context[:800]}

Generate a JSON object with ONLY these keys:
1. "portfolio_projects": array of 2-3 project objects with fields: title, one_liner, description, tech_stack(array), difficulty, time_estimate, recruiter_appeal
2. "milestones": array of {months} milestone objects with fields: month(int), description(string, 1 sentence)

Return ONLY valid JSON."""

    llm_response = await call_nemotron(llm_prompt, ROADMAP_SYSTEM, temperature=0.7, max_tokens=2000)
    llm_data = extract_json(llm_response) or {}

    portfolio_projects = llm_data.get("portfolio_projects", [
        {
            "title": f"{role} Showcase Project",
            "one_liner": f"Demonstrates {missing_skills[0] if missing_skills else role} skills end-to-end",
            "description": f"A comprehensive project that hiring managers love to see for {role} candidates.",
            "tech_stack": missing_skills[:4],
            "difficulty": "Intermediate",
            "time_estimate": "2 weeks",
            "recruiter_appeal": "Shows real-world application of key skills",
        }
    ])

    milestones = llm_data.get("milestones", [
        {"month": m, "description": f"Month {m}: Proficient in {critical_missing[(m-1)*skills_per_month:(m)*skills_per_month]}"}
        for m in range(1, months + 1)
    ])

    # Build OpenNote markdown export
    opennote_md = _build_markdown_export(role, phases, portfolio_projects, milestones)

    return {
        "role": role,
        "months": months,
        "user_skills": user_skills,
        "missing_skills": missing_skills,
        "readiness_pct": readiness_pct,
        "phases": phases,
        "portfolio_projects": portfolio_projects,
        "interview_prep": {
            "start_month": max(1, months - 1),
            "platforms": [p for p in PRACTICE_PLATFORMS["interviews"]],
            "focus_skills": missing_skills[:5],
            "question_types": ["coding", "technical_concepts", "system_design", "behavioral"],
        },
        "networking": {
            "communities": [
                {"name": "r/" + role.replace(" ", ""), "url": f"https://reddit.com/r/{role.replace(' ', '').replace('/', '')}"},
            ],
            "discord_servers": discord_servers,
            "collab_platforms": collab_platforms,
            "opennote": {
                "title": f"{role} Career Roadmap",
                "url": "https://opennote.me",
                "description": "Export this roadmap to OpenNote for collaborative note-taking",
            },
        },
        "milestones": milestones,
        "export": {
            "opennote_markdown": opennote_md,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def _build_markdown_export(role: str, phases: list, projects: list, milestones: list) -> str:
    lines = [f"# {role} — Career Roadmap\n", f"Generated by SkillBridge AI\n"]
    for phase in phases:
        lines.append(f"\n## Month {phase['month']}: {phase['title']}\n")
        for week in phase.get("weeks", []):
            lines.append(f"\n### Week {week['week']}: {', '.join(week['skills_focus'])}\n")
            lines.append(f"**Daily Plan:** {week['daily_plan']}\n")
            lines.append("**Resources:**\n")
            for r in week.get("resources", [])[:3]:
                lines.append(f"- [{r.get('title', '')}]({r.get('url', '')})\n")
            if week.get("project"):
                p = week["project"]
                lines.append(f"\n**Project:** {p['title']} — {p['description']}\n")
    lines.append("\n## Portfolio Projects\n")
    for p in projects:
        lines.append(f"\n### {p.get('title', '')}\n")
        lines.append(f"{p.get('description', '')}\n")
    return "".join(lines)
