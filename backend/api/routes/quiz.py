from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.session import get_db
from ...services.llm import generate_quiz_questions
from ...services.analytics import track
from ...core.config import BADGES
from ...db.models import User
from ..deps import get_optional_user, get_current_user

router = APIRouter(prefix="/quiz", tags=["quiz"])


class SubmitRequest(BaseModel):
    answers: list[dict]  # [{question_id, chosen_index, correct_index}]
    role: str = ""


@router.get("/questions")
async def get_quiz_questions(
    role: str = Query(...),
    skills: str = Query("", description="Comma-separated skills"),
    count: int = Query(15, ge=5, le=20),
    user: User | None = Depends(get_optional_user),
):
    skills_list = [s.strip() for s in skills.split(",") if s.strip()] if skills else []
    questions = await generate_quiz_questions(role, skills_list, count)
    return {"questions": questions, "count": len(questions)}


@router.post("/submit")
async def submit_quiz(
    body: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    if not body.answers:
        return {"score": 0, "xp_earned": 0, "badges_unlocked": []}

    correct = sum(1 for a in body.answers if a.get("chosen_index") == a.get("correct_index"))
    total = len(body.answers)
    score_pct = round((correct / total) * 100, 1)
    xp_earned = correct * 10

    badges_unlocked = []
    if user:
        user.xp = (user.xp or 0) + xp_earned
        badges = list(user.badges or [])
        if score_pct >= 80 and "quiz_ace" not in badges:
            badges.append("quiz_ace")
            badges_unlocked.append("quiz_ace")
            user.xp += BADGES["quiz_ace"]["xp"]
        user.badges = badges
        await db.commit()
        track(str(user.id), "quiz_submitted", {"score_pct": score_pct, "role": body.role, "xp_earned": xp_earned})

    return {
        "score_pct": score_pct,
        "correct": correct,
        "total": total,
        "xp_earned": xp_earned,
        "badges_unlocked": badges_unlocked,
    }
