"""Async database session management.

Supabase connection pooling: Use the Transaction pooler (port 6543) or append ?pgbouncer=true
to your connection string for serverless. Direct connections (port 5432) work for migrations.
"""
from collections.abc import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# DATABASE_URL from env overrides config (Supabase provides this). For serverless,
# use Supabase's pooler URL (port 6543 or ?pgbouncer=true) to avoid connection limits.
_db_url = os.getenv("DATABASE_URL") or settings.database_url
if _db_url.startswith("postgres://"):
    _db_url = "postgresql+asyncpg://" + _db_url[11:]
elif _db_url.startswith("postgresql://") and "+asyncpg" not in _db_url:
    _db_url = _db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(
    _db_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=2,
    max_overflow=4,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def init_db() -> None:
    """Verify database connectivity on startup."""
    async with engine.connect() as conn:
        await conn.run_sync(lambda _: None)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for async database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
