from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .models import Base
from ..core.config import get_settings

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        url = settings.database_url
        connect_args = {}
        # asyncpg doesn't accept sslmode in the URL; strip it and pass ssl via connect_args
        if "sslmode=require" in url:
            url = url.replace("?sslmode=require", "").replace("&sslmode=require", "")
            connect_args["ssl"] = True
        _engine = create_async_engine(url, echo=False, pool_pre_ping=True, connect_args=connect_args)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _SessionLocal


async def init_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
