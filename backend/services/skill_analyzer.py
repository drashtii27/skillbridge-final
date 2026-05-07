from ..core.config import ROLE_SKILLS, get_settings
from .llm import get_market_insight


import re as _re

def normalize(skill: str) -> str:
    return skill.lower().strip()

def _tokens(skill: str) -> set[str]:
    """Split skill into lowercase alphabetic tokens, min length 3."""
    return {t for t in _re.split(r'[^a-z]+', skill.lower()) if len(t) >= 3}


def match_skills(user_skills: list[str], role: str) -> dict:
    role_data = ROLE_SKILLS.get(role, {})
    critical = [s for s in role_data.get("critical", [])]
    important = [s for s in role_data.get("important", [])]
    emerging = [s for s in role_data.get("emerging", [])]
    all_required = critical + important + emerging

    user_normalized = {normalize(s) for s in user_skills}
    user_token_sets = [_tokens(s) for s in user_skills]

    def skill_matched(skill: str) -> bool:
        sn = normalize(skill)
        # 1. Direct or substring match
        if sn in user_normalized or any(sn in un or un in sn for un in user_normalized):
            return True
        # 2. Token overlap with prefix matching (handles plurals/abbreviations)
        role_tokens = _tokens(skill)
        if not role_tokens:
            return False
        all_user_tokens: set[str] = set()
        for ut in user_token_sets:
            all_user_tokens |= ut
        for rt in role_tokens:
            for ut in all_user_tokens:
                # prefix match: "oscilloscope" matches "oscilloscopes", "pcb" matches "pcb"
                if rt.startswith(ut[:4]) or ut.startswith(rt[:4]):
                    if len(min(rt, ut, key=len)) >= 4:  # avoid matching tiny fragments
                        return True
        return False

    matched_critical = [s for s in critical if skill_matched(s)]
    matched_important = [s for s in important if skill_matched(s)]
    matched_emerging = [s for s in emerging if skill_matched(s)]

    gap_critical = [s for s in critical if not skill_matched(s)]
    gap_important = [s for s in important if not skill_matched(s)]
    gap_emerging = [s for s in emerging if not skill_matched(s)]

    total = len(all_required) or 1
    matched_count = len(matched_critical) * 3 + len(matched_important) * 2 + len(matched_emerging)
    max_possible = len(critical) * 3 + len(important) * 2 + len(emerging)
    readiness_pct = round((matched_count / (max_possible or 1)) * 100, 1)

    matched = (
        [{"skill": s, "category": "Critical", "importance_score": 100} for s in matched_critical]
        + [{"skill": s, "category": "Important", "importance_score": 70} for s in matched_important]
        + [{"skill": s, "category": "Emerging", "importance_score": 50} for s in matched_emerging]
    )
    gaps = (
        [{"skill": s, "category": "Critical", "importance_score": 100} for s in gap_critical]
        + [{"skill": s, "category": "Important", "importance_score": 70} for s in gap_important]
        + [{"skill": s, "category": "Emerging", "importance_score": 50} for s in gap_emerging]
    )

    category_chart = {
        "categories": ["Critical", "Important", "Emerging"],
        "have": [len(matched_critical), len(matched_important), len(matched_emerging)],
        "need": [len(gap_critical), len(gap_important), len(gap_emerging)],
    }

    return {
        "role": role,
        "readiness_pct": readiness_pct,
        "gap_pct": round(100 - readiness_pct, 1),
        "matched": matched,
        "gaps": gaps,
        "category_chart": category_chart,
    }


async def analyze_gap(role: str, user_skills: list[str], rag_context: str = "") -> dict:
    result = match_skills(user_skills, role)
    insight = await get_market_insight(role, user_skills, rag_context)
    result["market_insight"] = insight
    return result
