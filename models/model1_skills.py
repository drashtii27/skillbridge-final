"""
MODEL 1: Skills Intelligence (100% FREE)
- GLiNER v0.5 (free, runs locally) for skill extraction
- HuggingFace Inference API (free tier) for market analysis
- Rule-based gap analysis (no API needed)
"""
import json, os, requests
from typing import List, Dict
from loguru import logger
from config import ROLE_SKILLS, NOISE, HF_TOKEN, OPENAI_API_KEY, ALL_ROLES, get_role_skills
from utils import is_noise, filter_skills


class SkillExtractor:
    """Extract skills from text using GLiNER (free, local)."""
    def __init__(self):
        self.model = None
        self._labels = ["programming language","framework","library","database","cloud platform",
                        "tool","technology","technical skill","methodology","software","algorithm"]

    def load(self):
        try:
            from gliner import GLiNER
            self.model = GLiNER.from_pretrained("knowledgator/gliner-multitask-large-v0.5")
            logger.info("GLiNER loaded ✓")
        except Exception as e:
            logger.warning(f"GLiNER unavailable ({e}). Using keyword fallback.")

    def extract(self, text, threshold=0.35):
        if self.model is None: self.load()
        if self.model is None: return self._fallback(text)
        try:
            ents = self.model.predict_entities(text, self._labels, threshold=threshold, flat_ner=True)
            seen, results = set(), []
            for e in ents:
                n = e["text"].strip()
                if n.lower() not in seen and not is_noise(n):
                    seen.add(n.lower())
                    results.append({"skill": n, "confidence": round(float(e["score"]),3), "type": e["label"]})
            results.sort(key=lambda x: x["confidence"], reverse=True)
            return results
        except Exception as e:
            logger.error(f"GLiNER error: {e}")
            return self._fallback(text)

    def _fallback(self, text):
        all_s = set()
        for rd in ROLE_SKILLS.values():
            for v in rd.values():
                for s in v:
                    for p in s.replace("(", ",").replace(")", "").replace("/", ",").split(","):
                        p = p.strip()
                        if p and len(p) > 2: all_s.add(p.lower())
        tl = text.lower()
        return [{"skill": s.title(), "confidence": 0.6, "type": "keyword"} for s in all_s if s in tl and not is_noise(s)]


class SkillGapAnalyzer:
    """Analyze gap between user skills and role requirements (FREE, no API)."""
    def analyze(self, target_role, user_skills):
        rd = ROLE_SKILLS.get(target_role, {})
        if not rd:
            for r in ALL_ROLES:
                if target_role.lower() in r.lower() or r.lower() in target_role.lower():
                    rd = ROLE_SKILLS[r]; target_role = r; break

        user_lower = set(s.lower().strip() for s in user_skills)

        # Score: critical=100, important=70, emerging=50
        scores = {"critical": 100, "important": 70, "emerging_2025": 50}
        labels = {"critical": "🔴 Critical", "important": "🟡 Important", "emerging_2025": "🟢 Emerging 2025"}

        all_matched, all_gaps = [], []
        cat_have, cat_need = {"Critical":0,"Important":0,"Emerging 2025":0}, {"Critical":0,"Important":0,"Emerging 2025":0}
        cat_labels = {"critical":"Critical","important":"Important","emerging_2025":"Emerging 2025"}

        for cat_key in ["critical", "important", "emerging_2025"]:
            skill_list = rd.get(cat_key, [])
            score = scores[cat_key]
            label = labels[cat_key]
            cl = cat_labels[cat_key]

            for skill in skill_list:
                found = any(us in skill.lower() or skill.lower() in us for us in user_lower)
                entry = {
                    "skill": skill,
                    "importance": label,
                    "importance_score": score,
                    "category": cl,
                    "status": "✅ You Have" if found else "❌ Need to Learn",
                }
                if found:
                    all_matched.append(entry)
                    cat_have[cl] += 1
                else:
                    all_gaps.append(entry)
                    cat_need[cl] += 1

        # Sort gaps by importance score (critical first)
        all_gaps.sort(key=lambda x: x["importance_score"], reverse=True)

        total = len(all_matched) + len(all_gaps)

        # Build per-skill bar chart data (specific skill names with scores)
        skill_chart = []
        for g in all_gaps:
            skill_chart.append({"Skill": g["skill"], "Importance Score": g["importance_score"], "Category": g["category"]})
        for m in all_matched:
            skill_chart.append({"Skill": m["skill"], "Importance Score": m["importance_score"], "Category": m["category"]})

        return {
            "role": target_role,
            "matched": all_matched,
            "gaps": all_gaps,
            "critical_gaps": [g for g in all_gaps if g["category"] == "Critical"],
            "important_gaps": [g for g in all_gaps if g["category"] == "Important"],
            "emerging_gaps": [g for g in all_gaps if g["category"] == "Emerging 2025"],
            "readiness_pct": round(len(all_matched)/max(1,total)*100, 1),
            "gap_pct": round(len(all_gaps)/max(1,total)*100, 1),
            "total_required": total,
            "category_chart": {
                "categories": ["Critical","Important","Emerging 2025"],
                "have": [cat_have["Critical"], cat_have["Important"], cat_have["Emerging 2025"]],
                "need": [cat_need["Critical"], cat_need["Important"], cat_need["Emerging 2025"]],
            },
            "skill_chart": skill_chart,  # per-skill with names and scores
        }


class JobMarketAnalyzer:
    """Analyze job market using FREE HuggingFace Inference API or OpenAI."""
    def analyze(self, role, user_skills, gap_data):
        # Try OpenAI first (if user has key), then HF free, then offline
        if OPENAI_API_KEY:
            return self._via_openai(role, user_skills, gap_data)
        if HF_TOKEN:
            return self._via_hf(role, user_skills, gap_data)
        return self._offline(role, gap_data)

    def _via_openai(self, role, user_skills, gap_data):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            prompt = self._build_prompt(role, user_skills, gap_data)
            r = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"user","content":prompt}], max_tokens=500)
            return r.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI market: {e}")
            return self._offline(role, gap_data)

    def _via_hf(self, role, user_skills, gap_data):
        """Use FREE HuggingFace Inference API."""
        try:
            prompt = self._build_prompt(role, user_skills, gap_data)
            r = requests.post("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                headers={"Authorization": f"Bearer {HF_TOKEN}"},
                json={"inputs": f"<s>[INST] {prompt} [/INST]", "parameters": {"max_new_tokens": 500, "temperature": 0.7}},
                timeout=60)
            r.raise_for_status()
            data = r.json()
            if isinstance(data, list) and data:
                text = data[0].get("generated_text", "")
                # Extract only the response after [/INST]
                if "[/INST]" in text:
                    text = text.split("[/INST]")[-1].strip()
                return text
            return self._offline(role, gap_data)
        except Exception as e:
            logger.error(f"HF market: {e}")
            return self._offline(role, gap_data)

    def _build_prompt(self, role, user_skills, gap_data):
        crit = ", ".join(s["skill"] for s in gap_data.get("critical_gaps", []))
        return (f"You are a 2025 career expert. Analyze the job market for '{role}'. "
                f"User knows: {', '.join(user_skills[:8])}. Missing critical: {crit}. "
                f"Give: 1) Market demand 2) Top 5 in-demand skills 3) What to learn first 4) 2025 trends 5) Quick wins. "
                f"Be specific with numbers and tools. Max 250 words.")

    def _offline(self, role, gap_data):
        crit = gap_data.get("critical_gaps", [])
        top = ", ".join(s["skill"] for s in crit[:3]) if crit else "N/A"
        return (f"**{role} – 2025 Market Snapshot**\n\n"
                f"Readiness: {gap_data.get('readiness_pct',0)}%. "
                f"**Priority skills:** {top}.\n\n"
                f"Focus on critical gaps first, then emerging 2025 technologies.\n\n"
                f"*Add HF_TOKEN to .env for free AI-powered market analysis.*")
