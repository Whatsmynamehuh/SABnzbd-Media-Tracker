"""
Database configuration and session management.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
import os

# Base class for all models
Base = declarative_base()

# Database configuration
DATABASE_DIR = os.getenv("DATABASE_DIR", "./data")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATABASE_DIR}/media_tracker.db")


class AsyncDatabase:
    """Async database manager with connection pooling."""

    def __init__(self, database_url: str = DATABASE_URL):
        """Initialize database engine and session factory."""
        # Ensure data directory exists
        os.makedirs(DATABASE_DIR, exist_ok=True)

        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,   # Recycle connections after 1 hour
        )

        self.async_session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def init_db(self) -> None:
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session."""
        async with self.async_session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close(self) -> None:
        """Close database engine."""
        await self.engine.dispose()


# Global database instance
db = AsyncDatabase()
