from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger
import os

from .core.config import get_settings
from .db.session import init_db
from .api.routes import auth, resume, skills, roadmap, interview, jobs, quiz
from .api.deps import get_current_user
from .db.models import User


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("SkillBridge API starting...")
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.warning(f"DB init warning: {e}")
    try:
        from .services.rag import get_client
        get_client()
        logger.info("ChromaDB initialized")
    except Exception as e:
        logger.warning(f"ChromaDB init warning: {e}")
    # Pre-warm GLiNER in background so first resume upload is fast
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        from .services.llm import _extract_skills_gliner
        loop.run_in_executor(None, lambda: _extract_skills_gliner("Python SQL Machine Learning"))
        logger.info("GLiNER pre-warming started in background")
    except Exception as e:
        logger.warning(f"GLiNER pre-warm skipped: {e}")
    yield
    logger.info("SkillBridge API shutting down")


settings = get_settings()

app = FastAPI(
    title="SkillBridge AI",
    description="AI-powered career development platform",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for evaluation charts
os.makedirs("static/charts", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Routers
app.include_router(auth.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(skills.router, prefix="/api")
app.include_router(roadmap.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
app.include_router(quiz.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": settings.ollama_model, "version": "2.0.0"}


@app.get("/api/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "xp": user.xp,
        "badges": user.badges or [],
        "avatar_color": user.avatar_color,
    }


@app.post("/api/admin/reset-db")
async def reset_db():
    """Drop and recreate all tables. Use once to fix stale Neon schema."""
    from .db.session import get_engine
    from .db.models import Base
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema reset complete")
    return {"status": "ok", "message": "All tables dropped and recreated"}


@app.get("/api/roles")
async def list_roles():
    from .core.config import ALL_ROLES, ROLE_SKILLS
    return {
        "roles": ALL_ROLES,
        "role_details": {
            r: {
                "critical_count": len(ROLE_SKILLS[r].get("critical", [])),
                "sample_skills": ROLE_SKILLS[r].get("critical", [])[:4],
            }
            for r in ALL_ROLES
        },
    }
