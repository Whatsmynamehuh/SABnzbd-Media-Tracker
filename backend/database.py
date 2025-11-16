from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

Base = declarative_base()


class Download(Base):
    __tablename__ = "downloads"

    id = Column(String, primary_key=True)  # SABnzbd NZO ID
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # downloading, queued, completed, failed
    progress = Column(Float, default=0.0)  # 0-100
    size_total = Column(Float, nullable=True)  # in MB
    size_left = Column(Float, nullable=True)  # in MB
    time_left = Column(String, nullable=True)
    speed = Column(Float, nullable=True)  # MB/s
    category = Column(String, nullable=True)
    priority = Column(String, nullable=True)  # Force, High, Normal, Low
    queue_position = Column(Integer, nullable=True)  # Position in queue (1, 2, 3...)

    # Media info from Radarr/Sonarr
    media_type = Column(String, nullable=True)  # movie or tv
    media_title = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    arr_instance = Column(String, nullable=True)  # Which Radarr/Sonarr instance
    poster_attempted = Column(Boolean, default=False)  # Have we tried fetching poster?

    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Failed downloads
    failed = Column(Boolean, default=False)
    failure_reason = Column(Text, nullable=True)


class AsyncDatabase:
    def __init__(self, database_url: str = "sqlite+aiosqlite:///./media_tracker.db"):
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """Initialize database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        async with self.async_session() as session:
            yield session


# Global database instance
db = AsyncDatabase()
