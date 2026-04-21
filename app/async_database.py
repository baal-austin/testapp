# async_database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from typing import AsyncGenerator
from app.config import settings


def get_async_database_engine():
    """创建异步数据库引擎"""
    if settings.DATABASE_TYPE == "postgresql":
        # 异步 PostgreSQL 需要 asyncpg 驱动
        database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

        engine = create_async_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=settings.POSTGRES_POOL_SIZE,
            max_overflow=settings.POSTGRES_MAX_OVERFLOW,
            pool_timeout=settings.POSTGRES_POOL_TIMEOUT,
            pool_recycle=3600,
            echo=settings.POSTGRES_ECHO or settings.DEBUG,
        )
    else:
        # SQLite 异步支持有限，这里用 aiosqlite
        database_url = settings.DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            connect_args={"check_same_thread": False}
        )

    return engine


# 创建异步引擎
async_engine = get_async_database_engine()

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """异步数据库会话依赖项"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()