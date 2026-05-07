"""
SkillBridge AI – Database Module (PostgreSQL on Neon Cloud)
Tables: jobs, interview_questions, skills, evaluation_runs, roadmaps
Full ETL pipeline: scrape → clean → transform → load to Postgres
"""
from datetime import datetime
from sqlalchemy import (create_engine, Column, Integer, String, Float, Text,
                        DateTime, Boolean, JSON, Index, text)
from sqlalchemy.orm import declarative_base, sessionmaker
from loguru import logger
from config import PG_URL

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    source = Column(String(50), index=True)
    role = Column(String(200), index=True)
    title = Column(String(500))
    company = Column(String(300))
    location = Column(String(300))
    description = Column(Text)
    skills_extracted = Column(Text)  # JSON array
    url = Column(String(1000))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    hash = Column(String(64), unique=True)

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"
    id = Column(Integer, primary_key=True)
    source = Column(String(50), index=True)
    role = Column(String(200), index=True)
    question = Column(Text)
    difficulty = Column(String(50))
    tags = Column(Text)
    url = Column(String(1000))
    scraped_at = Column(DateTime, default=datetime.utcnow)
    hash = Column(String(64), unique=True)

class SkillRecord(Base):
    __tablename__ = "skills_taxonomy"
    id = Column(Integer, primary_key=True)
    skill_name = Column(String(300), index=True)
    category = Column(String(100))  # critical/important/emerging
    domain = Column(String(200))    # role name
    importance_score = Column(Float, default=0.0)

class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"
    id = Column(Integer, primary_key=True)
    model_name = Column(String(200))
    metrics = Column(JSON)
    samples = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class RoadmapRecord(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True)
    target_role = Column(String(200))
    user_skills = Column(Text)
    missing_skills = Column(Text)
    roadmap_text = Column(Text)
    model_used = Column(String(200))
    months = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_engine():
    if not PG_URL: return None
    return create_engine(PG_URL, pool_pre_ping=True, pool_size=5)

def init_db():
    """Create tables if they don't exist (keeps existing data)."""
    engine = get_engine()
    if engine:
        Base.metadata.create_all(engine)
        logger.info("PostgreSQL tables ready ✓")
        return engine
    logger.warning("PG_URL not set – database disabled")
    return None

def get_session():
    engine = get_engine()
    if not engine: return None
    return sessionmaker(bind=engine)()

def load_jobs_to_db(jobs_data):
    """ETL: Batch-load NEW jobs (skips duplicates, accumulates over runs)."""
    import hashlib, json
    engine = get_engine()
    if not engine: return 0
    # Get existing hashes to skip duplicates
    with engine.connect() as conn:
        existing = set(r[0] for r in conn.execute(text("SELECT hash FROM jobs")).fetchall())
    logger.info(f"  Existing jobs in DB: {len(existing)}")
    rows = []
    seen = set()
    for job in jobs_data:
        h = hashlib.sha256(f"{job.get('title','')}_{job.get('company','')}_{job.get('role','')}".encode()).hexdigest()
        if h not in seen and h not in existing:
            seen.add(h)
            rows.append({
                "source": job.get("source","")[:50], "role": job.get("role","")[:200],
                "title": job.get("title","")[:500], "company": job.get("company","")[:300],
                "location": job.get("location","")[:300], "description": job.get("description","")[:5000],
                "skills_extracted": json.dumps(job.get("skills_extracted",[])),
                "url": job.get("url","")[:1000], "hash": h,
            })
    if not rows:
        logger.info("  No new jobs to insert (all duplicates)")
        return 0
    with engine.connect() as conn:
        for i in range(0, len(rows), 500):
            chunk = rows[i:i+500]
            conn.execute(Job.__table__.insert(), chunk)
            conn.commit()
            logger.info(f"  Batch {i//500+1}: {len(chunk)} NEW jobs inserted")
    logger.info(f"Loaded {len(rows)} NEW jobs to PostgreSQL")
    return len(rows)

def load_questions_to_db(questions_data):
    """ETL: Batch-load NEW questions (skips duplicates, accumulates)."""
    import hashlib, json
    engine = get_engine()
    if not engine: return 0
    with engine.connect() as conn:
        existing = set(r[0] for r in conn.execute(text("SELECT hash FROM interview_questions")).fetchall())
    logger.info(f"  Existing questions in DB: {len(existing)}")
    rows = []
    seen = set()
    for q in questions_data:
        h = hashlib.sha256(q.get("question","").encode()).hexdigest()
        if h not in seen and h not in existing:
            seen.add(h)
            rows.append({
                "source": q.get("source","")[:50], "role": q.get("role","")[:200],
                "question": q.get("question","")[:5000], "difficulty": q.get("difficulty","")[:50],
                "tags": json.dumps(q.get("tags",[])), "url": q.get("url","")[:1000], "hash": h,
            })
    if not rows:
        logger.info("  No new questions to insert")
        return 0
    with engine.connect() as conn:
        for i in range(0, len(rows), 500):
            chunk = rows[i:i+500]
            conn.execute(InterviewQuestion.__table__.insert(), chunk)
            conn.commit()
            logger.info(f"  Batch {i//500+1}: {len(chunk)} NEW questions inserted")
    logger.info(f"Loaded {len(rows)} NEW questions to PostgreSQL")
    return len(rows)

def load_skills_taxonomy(role_skills_dict):
    """Load skills taxonomy into PostgreSQL."""
    session = get_session()
    if not session: return
    scores = {"critical": 100, "important": 70, "emerging_2025": 50}
    for role, categories in role_skills_dict.items():
        for cat, skills in categories.items():
            for skill in skills:
                if not session.query(SkillRecord).filter_by(skill_name=skill, domain=role).first():
                    session.add(SkillRecord(
                        skill_name=skill, category=cat, domain=role,
                        importance_score=scores.get(cat, 50),
                    ))
    session.commit(); session.close()
    logger.info("Skills taxonomy loaded to PostgreSQL")

def save_evaluation(model_name, metrics, samples):
    """Save evaluation run to PostgreSQL."""
    session = get_session()
    if not session: return
    session.add(EvaluationRun(model_name=model_name, metrics=metrics, samples=samples))
    session.commit(); session.close()

def run_etl_pipeline(jobs, questions):
    """Full ETL: init DB → load jobs → load questions → load taxonomy."""
    from config import ROLE_SKILLS
    engine = init_db()
    if not engine:
        logger.warning("ETL skipped – no database connection")
        return
    j = load_jobs_to_db(jobs)
    q = load_questions_to_db(questions)
    load_skills_taxonomy(ROLE_SKILLS)
    logger.info(f"ETL complete: {j} jobs, {q} questions loaded")

def get_db_stats():
    """Get record counts from PostgreSQL."""
    session = get_session()
    if not session: return {"status": "disconnected"}
    stats = {
        "jobs": session.query(Job).count(),
        "questions": session.query(InterviewQuestion).count(),
        "skills": session.query(SkillRecord).count(),
        "evaluations": session.query(EvaluationRun).count(),
        "roadmaps": session.query(RoadmapRecord).count(),
        "status": "connected",
    }
    session.close()
    return stats
