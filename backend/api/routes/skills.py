from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ...services.skill_analyzer import analyze_gap, match_skills
from ...services.rag import retrieve_skill_context
from ...services.analytics import track
from ...db.models import User
from ...core.config import ROLE_SKILLS
from ..deps import get_optional_user

router = APIRouter(prefix="/skills", tags=["skills"])


class AnalyzeRequest(BaseModel):
    role: str
    user_skills: list[str]
    months: int = 3


class SuggestRolesRequest(BaseModel):
    user_skills: list[str]


@router.post("/suggest-roles")
async def suggest_roles(body: SuggestRolesRequest):
    """Score every role against the extracted skills and return the top 5 matches."""
    scored = []
    for role in ROLE_SKILLS:
        result = match_skills(body.user_skills, role)
        scored.append({
            "role": role,
            "readiness_pct": result["readiness_pct"],
            "matched_count": len(result["matched"]),
            "gap_count": len(result["gaps"]),
            "matched_skills": [m["skill"] for m in result["matched"][:4]],
        })
    scored.sort(key=lambda x: x["readiness_pct"], reverse=True)
    return {"suggestions": scored[:6]}


@router.post("/analyze")
async def analyze_skills(
    body: AnalyzeRequest,
    user: User | None = Depends(get_optional_user),
):
    rag_context = retrieve_skill_context(body.user_skills, body.role, n_results=3)
    result = await analyze_gap(body.role, body.user_skills, rag_context)
    result["months"] = body.months

    if user:
        track(str(user.id), "skills_analyzed", {"role": body.role, "readiness_pct": result["readiness_pct"]})

    return result
