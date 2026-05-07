from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ...services.llm import generate_interview_questions, get_adaptive_question
from ...services.rag import retrieve_similar_questions
from ...services.analytics import track
from ...db.models import User
from ..deps import get_optional_user

router = APIRouter(prefix="/interview", tags=["interview"])


class QuestionsRequest(BaseModel):
    role: str
    skills_to_test: list[str]
    count: int = 10


class AdaptiveRequest(BaseModel):
    role: str
    skills: list[str]
    step: int = 0


@router.post("/questions")
async def get_questions(
    body: QuestionsRequest,
    user: User | None = Depends(get_optional_user),
):
    rag_context = retrieve_similar_questions(body.role, body.skills_to_test)
    questions = await generate_interview_questions(body.role, body.skills_to_test, body.count, rag_context)
    if user:
        track(str(user.id), "interview_questions_generated", {"role": body.role, "count": len(questions)})
    return {"questions": questions, "count": len(questions), "role": body.role}


@router.post("/adaptive")
async def adaptive_question(
    body: AdaptiveRequest,
    user: User | None = Depends(get_optional_user),
):
    question = await get_adaptive_question(body.role, body.skills, body.step)
    return question
