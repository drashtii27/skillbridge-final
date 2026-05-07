"""
MODEL 3: Project Recommender (FREE)
- HuggingFace Inference API (Qwen2.5-72B or Mistral-7B, free tier)
- Falls back to templates
"""
import json, re, requests
from typing import List, Dict
from loguru import logger
from config import HF_TOKEN, OPENAI_API_KEY, ANTHROPIC_API_KEY, ROLE_SKILLS


class ProjectRecommender:
    def generate(self, role, user_skills, missing_skills, count=5):
        from config import DEEPSEEK_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
        if ANTHROPIC_API_KEY:
            return self._via_claude(role, user_skills, missing_skills, count)
        if OPENAI_API_KEY:
            return self._via_openai(role, user_skills, missing_skills, count)
        if DEEPSEEK_API_KEY:
            return self._via_deepseek(role, user_skills, missing_skills, count)
        try:
            if requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2).status_code == 200:
                return self._via_ollama(role, user_skills, missing_skills, count)
        except: pass
        if HF_TOKEN:
            return self._via_hf(role, user_skills, missing_skills, count)
        return self._offline(role, missing_skills, count)

    def _via_deepseek(self, role, us, ms, count):
        try:
            from openai import OpenAI
            from config import DEEPSEEK_API_KEY
            client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
            r = client.chat.completions.create(model="deepseek-chat",
                messages=[{"role":"system","content":"Return ONLY valid JSON array."},
                          {"role":"user","content":self._prompt(role, us, ms, count)}],
                max_tokens=2500, temperature=0.7)
            return self._parse(r.choices[0].message.content, "deepseek-v3")
        except Exception as e:
            logger.error(f"DeepSeek projects: {e}")
            return self._offline(role, ms, count)

    def _via_ollama(self, role, us, ms, count):
        from config import OLLAMA_BASE_URL, OLLAMA_MODEL
        try:
            r = requests.post(f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": self._prompt(role, us, ms, count),
                      "stream": False, "options":{"temperature":0.7}}, timeout=120)
            r.raise_for_status()
            return self._parse(r.json().get("response",""), f"ollama-{OLLAMA_MODEL}")
        except Exception as e:
            logger.error(f"Ollama projects: {e}")
            return self._offline(role, ms, count)

    def _via_claude(self, role, us, ms, count):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            prompt = self._prompt(role, us, ms, count)
            r = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=3000, messages=[{"role":"user","content":prompt}])
            return self._parse(r.content[0].text, "claude-3.5-sonnet")
        except Exception as e:
            logger.error(f"Claude projects: {e}")
            return self._via_hf(role, us, ms, count) if HF_TOKEN else self._offline(role, ms, count)

    def _via_openai(self, role, us, ms, count):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            r = client.chat.completions.create(model="gpt-4o-mini",
                messages=[{"role":"system","content":"Return ONLY valid JSON array."},
                          {"role":"user","content":self._prompt(role, us, ms, count)}],
                max_tokens=2500, temperature=0.7)
            return self._parse(r.choices[0].message.content, "gpt-4o-mini")
        except Exception as e:
            logger.error(f"OpenAI projects: {e}")
            return self._via_hf(role, us, ms, count) if HF_TOKEN else self._offline(role, ms, count)

    def _via_hf(self, role, us, ms, count):
        """FREE HuggingFace Inference API."""
        try:
            prompt = (f"Generate {min(count,4)} resume projects for '{role}'. "
                      f"Skills to showcase: {', '.join(ms[:6])}. "
                      f"For each: title, one_liner, description, tech_stack, skills_demonstrated, "
                      f"difficulty, time_estimate, recruiter_appeal. Return ONLY JSON array.")
            r = requests.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": f"<s>[INST] {prompt} [/INST]", "parameters": {"max_new_tokens": 2000, "temperature": 0.7}},
                timeout=90)
            r.raise_for_status()
            data = r.json()
            text = data[0].get("generated_text", "") if isinstance(data, list) else ""
            if "[/INST]" in text: text = text.split("[/INST]")[-1].strip()
            return self._parse(text, "mistral-7b-free")
        except Exception as e:
            logger.error(f"HF projects: {e}")
            return self._offline(role, ms, count)

    def _prompt(self, role, us, ms, count):
        return f"""Generate {count} RESUME-WORTHY PROJECTS for "{role}" in 2025.
Current skills: {', '.join(us[:8])}
Skills to demonstrate: {', '.join(ms[:8])}
Return ONLY JSON array: [{{"title":"...","one_liner":"...","description":"...","tech_stack":["..."],"features":["..."],"skills_demonstrated":["..."],"difficulty":"Beginner|Intermediate|Advanced","time_estimate":"...","recruiter_appeal":"..."}}]
Use 2025 tech. Be specific. No generic projects. For non-tech: analyses, reports, dashboards."""

    def _parse(self, text, model_name):
        text = text.strip()
        if text.startswith("```"): text = text.split("```")[1].lstrip("json").strip()
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            try:
                projects = json.loads(match.group())
                for p in projects: p["model"] = model_name
                return projects
            except json.JSONDecodeError:
                pass
        logger.warning(f"Could not parse projects JSON from {model_name}")
        return self._offline("", [], 3)

    def _offline(self, role, ms, count):
        from config.knowledge_base import get_project, get_resource
        diffs = ["Beginner","Intermediate","Intermediate","Advanced","Advanced"]
        projects = []
        for i, skill in enumerate(ms[:count]):
            proj = get_project(skill, role)
            res = get_resource(skill)
            projects.append({
                "title": proj["title"],
                "one_liner": f"{proj['desc'][:80]}...",
                "description": proj["desc"],
                "tech_stack": proj["stack"],
                "features": [
                    f"Learn via: {', '.join(res['courses'][:2])}",
                    f"Practice: {res['practice']}",
                    f"Documentation: {res['docs']}",
                ],
                "skills_demonstrated": [skill],
                "difficulty": diffs[i % len(diffs)],
                "time_estimate": proj.get("time", "1-2 weeks"),
                "recruiter_appeal": f"Shows hands-on {skill} expertise with real deliverables for {role} role",
                "model": "knowledge_base",
            })
        return projects
        return projects
