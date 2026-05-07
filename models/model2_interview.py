"""
MODEL 2: Interview Intelligence (FREE)
- HuggingFace Inference API (Mistral-7B, free tier) for question generation
- Falls back to templates if API unavailable
"""
import json, requests
from typing import List, Dict
from loguru import logger
from config import HF_TOKEN, OPENAI_API_KEY, ROLE_SKILLS, get_role_skills


class InterviewQuestionGenerator:
    def generate(self, role, skills_to_test, count=15):
        from config import DEEPSEEK_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
        if OPENAI_API_KEY:
            return self._via_openai(role, skills_to_test, count)
        if DEEPSEEK_API_KEY:
            return self._via_deepseek(role, skills_to_test, count)
        if self._ollama_ok():
            return self._via_ollama(role, skills_to_test, count)
        if HF_TOKEN:
            return self._via_hf(role, skills_to_test, count)
        return self._offline(role, skills_to_test, count)

    def _ollama_ok(self):
        from config import OLLAMA_BASE_URL
        try: return requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2).status_code == 200
        except: return False

    def _via_deepseek(self, role, skills, count):
        try:
            from openai import OpenAI
            from config import DEEPSEEK_API_KEY
            client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
            rd = ROLE_SKILLS.get(role, {})
            prompt = f"""Generate {count} interview questions for "{role}" in 2025.
Skills to test: {', '.join(skills[:10])}
Critical: {', '.join(rd.get('critical',[])[:5])}
Return ONLY JSON array: [{{"question":"...","difficulty":"Easy|Medium|Hard","category":"Technical|Coding|System Design|Domain-Specific|Case Study","skills_tested":["..."],"answer_outline":["..."]}}]
NO soft skill questions. Be specific to {role}."""
            r = client.chat.completions.create(model="deepseek-chat",
                messages=[{"role":"system","content":"Return ONLY valid JSON array."},{"role":"user","content":prompt}],
                max_tokens=2500, temperature=0.7)
            text = r.choices[0].message.content.strip()
            if text.startswith("```"): text = text.split("```")[1].lstrip("json").strip()
            qs = json.loads(text)
            for q in qs: q["source"] = "deepseek-v3"
            return qs
        except Exception as e:
            logger.error(f"DeepSeek interview: {e}")
            return self._offline(role, skills, count)

    def _via_ollama(self, role, skills, count):
        from config import OLLAMA_BASE_URL, OLLAMA_MODEL
        try:
            prompt = f"""Generate {min(count,10)} technical interview questions for "{role}" testing: {', '.join(skills[:8])}.
For each: question, difficulty (Easy/Medium/Hard), category, skills_tested, answer_outline (2 bullets).
Return ONLY a JSON array. No markdown."""
            r = requests.post(f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options":{"temperature":0.7}},
                timeout=120)
            r.raise_for_status()
            text = r.json().get("response", "")
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                qs = json.loads(match.group())
                for q in qs: q["source"] = f"ollama-{OLLAMA_MODEL}"
                return qs[:count]
        except Exception as e:
            logger.error(f"Ollama interview: {e}")
        return self._offline(role, skills, count)

    def _via_openai(self, role, skills, count):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            rd = ROLE_SKILLS.get(role, {})
            prompt = f"""Generate {count} interview questions for "{role}" in 2025.
Skills to test: {', '.join(skills[:10])}
Critical: {', '.join(rd.get('critical',[])[:5])}
Return ONLY JSON array: [{{"question":"...","difficulty":"Easy|Medium|Hard","category":"Technical|Coding|System Design|Domain-Specific|Case Study","skills_tested":["..."],"answer_outline":["..."]}}]
NO soft skill questions. Be specific to {role}."""
            r = client.chat.completions.create(model="gpt-4o-mini",
                messages=[{"role":"system","content":"Return ONLY valid JSON array."},{"role":"user","content":prompt}],
                max_tokens=2500, temperature=0.7)
            text = r.choices[0].message.content.strip()
            if text.startswith("```"): text = text.split("```")[1].lstrip("json").strip()
            qs = json.loads(text)
            for q in qs: q["source"] = "gpt-4o-mini"
            return qs
        except Exception as e:
            logger.error(f"OpenAI interview: {e}")
            return self._via_hf(role, skills, count) if HF_TOKEN else self._offline(role, skills, count)

    def _via_hf(self, role, skills, count):
        """FREE HuggingFace Inference API."""
        try:
            prompt = (f"Generate {min(count,8)} technical interview questions for '{role}' testing these skills: "
                      f"{', '.join(skills[:8])}. For each give: question, difficulty (Easy/Medium/Hard), "
                      f"category, skills_tested, answer_outline (2 bullet points). "
                      f"Return ONLY a JSON array. No markdown.")
            r = requests.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": f"<s>[INST] {prompt} [/INST]", "parameters": {"max_new_tokens": 2000, "temperature": 0.7}},
                timeout=90)
            r.raise_for_status()
            data = r.json()
            text = data[0].get("generated_text", "") if isinstance(data, list) else ""
            if "[/INST]" in text: text = text.split("[/INST]")[-1].strip()
            if text.startswith("```"): text = text.split("```")[1].lstrip("json").strip()
            # Try to parse JSON
            import re
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                qs = json.loads(match.group())
                for q in qs: q["source"] = "mistral-7b-free"
                return qs[:count]
        except Exception as e:
            logger.error(f"HF interview: {e}")
        return self._offline(role, skills, count)

    def _offline(self, role, skills, count):
        templates = [
            ("Explain how {s} is used in a real {r} project.", "Medium", "Technical"),
            ("What are the key differences between {s} and alternatives in 2025?", "Medium", "Technical"),
            ("Design a system using {s} for {r} workflows.", "Hard", "System Design"),
            ("Write code demonstrating {s} for a common {r} problem.", "Medium", "Coding"),
            ("How has {s} evolved in 2025? Best practices?", "Medium", "Domain-Specific"),
            ("When would {s} NOT be the right choice?", "Hard", "Technical"),
            ("Walk through debugging a {s} issue in production.", "Hard", "Technical"),
        ]
        qs = []
        for i in range(min(count, len(skills)*2)):
            s = skills[i % len(skills)] if skills else "core concepts"
            t = templates[i % len(templates)]
            qs.append({"question": t[0].format(s=s, r=role), "difficulty": t[1],
                       "category": t[2], "skills_tested": [s],
                       "answer_outline": [f"Demonstrate {s} knowledge", "Give concrete examples"],
                       "source": "template"})
        return qs
