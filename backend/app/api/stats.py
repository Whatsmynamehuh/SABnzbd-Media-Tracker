"""
Statistics API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import db
from backend.app.schemas.download import StatsResponse

# Import will be provided by main.py
sync_service = None

router = APIRouter(prefix="/api", tags=["stats"])


async def get_db_session():
    """Dependency to get database session."""
    async for session in db.get_session():
        yield session


@router.get("/stats", response_model=StatsResponse)
async def get_stats(session: AsyncSession = Depends(get_db_session)):
    """Get download statistics."""
    all_downloads = await sync_service.get_all_downloads(session)

    downloading = len([d for d in all_downloads if d.status == "downloading"])
    queued = len([d for d in all_downloads if d.status == "queued"])
    completed = len([d for d in all_downloads if d.status == "completed"])
    failed = len([d for d in all_downloads if d.failed])

    # Calculate total speed
    total_speed = sum(d.speed or 0 for d in all_downloads if d.status == "downloading")

    return StatsResponse(
        downloading=downloading,
        queued=queued,
        completed=completed,
        failed=failed,
        total_speed=round(total_speed, 2)
    )
