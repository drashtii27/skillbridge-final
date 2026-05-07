from fastapi import APIRouter, Depends, Query
from ...services.jobs_fetcher import fetch_jobs_multi_source
from ...services.analytics import track
from ...db.models import User
from ..deps import get_optional_user

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/search")
async def search_jobs(
    role: str = Query(..., description="Target job role"),
    location: str = Query("us", description="Location (country code)"),
    count: int = Query(8, ge=1, le=20),
    user: User | None = Depends(get_optional_user),
):
    # Multi-source scraper: Remotive + Jobicy + The Muse + Adzuna (feedback: use scraper instead of Adzuna only)
    jobs = await fetch_jobs_multi_source(role, count_per_source=max(count // 3, 3))
    if user:
        track(str(user.id), "jobs_searched", {"role": role, "count": len(jobs)})
    return {"jobs": jobs, "count": len(jobs), "role": role}


@router.post("/click")
async def job_click(
    job_url: str,
    job_title: str = "",
    user: User | None = Depends(get_optional_user),
):
    if user:
        track(str(user.id), "job_clicked", {"url": job_url, "title": job_title})
        # Award badge
        from sqlalchemy import select
        from ...db.session import get_session_factory
        # simple fire-and-forget badge via analytics
    return {"ok": True}
