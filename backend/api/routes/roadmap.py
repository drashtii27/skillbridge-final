from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from ...db.session import get_db
from ...db.models import Roadmap, User, UserProgress
from ...services.roadmap_builder import generate_roadmap
from ...services.analytics import track
from ...core.config import get_settings
from ..deps import get_current_user, get_optional_user

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


class GenerateRequest(BaseModel):
    role: str
    user_skills: list[str]
    missing_skills: list[str]
    readiness_pct: float = 0.0
    months: int = 3


@router.post("/generate")
async def generate(
    body: GenerateRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    roadmap_json = await generate_roadmap(
        role=body.role,
        user_skills=body.user_skills,
        missing_skills=body.missing_skills,
        readiness_pct=body.readiness_pct,
        months=body.months,
    )
    settings = get_settings()
    roadmap_id = None

    # Try to persist — non-fatal if schema is stale (run /api/admin/reset-db once to fix)
    try:
        roadmap_row = Roadmap(
            user_id=user.id if user else None,
            target_role=body.role,
            user_skills=body.user_skills,
            missing_skills=body.missing_skills,
            roadmap_json=roadmap_json,
            months=body.months,
            model_used=settings.ollama_model,
        )
        db.add(roadmap_row)
        await db.commit()
        await db.refresh(roadmap_row)
        roadmap_id = roadmap_row.id

        if user:
            badges = list(user.badges or [])
            if "roadmap_generated" not in badges:
                badges.append("roadmap_generated")
                user.badges = badges
                user.xp = (user.xp or 0) + 100
                await db.commit()
    except Exception as e:
        await db.rollback()
        logger.warning(f"Roadmap DB save skipped (schema mismatch?): {e}. "
                       "Call POST /api/admin/reset-db to migrate the schema.")

    if user:
        track(str(user.id), "roadmap_generated", {"role": body.role, "months": body.months})

    return {**roadmap_json, "roadmap_id": roadmap_id}


@router.get("/{roadmap_id}")
async def get_roadmap(roadmap_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Roadmap).where(Roadmap.id == roadmap_id))
        roadmap = result.scalar_one_or_none()
        if not roadmap:
            raise HTTPException(status_code=404, detail="Roadmap not found")
        return {**roadmap.roadmap_json, "roadmap_id": roadmap.id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"DB unavailable: {e}")


@router.post("/{roadmap_id}/progress")
async def update_progress(
    roadmap_id: int,
    step_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        result = await db.execute(
            select(UserProgress).where(
                UserProgress.user_id == user.id,
                UserProgress.roadmap_id == roadmap_id,
            )
        )
        progress = result.scalar_one_or_none()
        if not progress:
            progress = UserProgress(user_id=user.id, roadmap_id=roadmap_id, completed_steps=[])
            db.add(progress)

        steps = list(progress.completed_steps or [])
        if step_id not in steps:
            steps.append(step_id)
            progress.completed_steps = steps
            user.xp = (user.xp or 0) + 10
            track(str(user.id), "milestone_completed", {"step": step_id, "roadmap_id": roadmap_id})

        badges = list(user.badges or [])
        if len(steps) >= 1 and "week_1_done" not in badges:
            badges.append("week_1_done")
            user.badges = badges
            user.xp = (user.xp or 0) + 200

        await db.commit()
        return {"completed_steps": steps, "xp": user.xp, "badges": user.badges}
    except Exception as e:
        await db.rollback()
        logger.warning(f"Progress update DB error: {e}")
        return {"completed_steps": [step_id], "xp": 0, "badges": []}
