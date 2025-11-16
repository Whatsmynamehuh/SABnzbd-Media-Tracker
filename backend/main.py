from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from typing import List
from pydantic import BaseModel
import uvicorn

from backend.database import db, Download
from backend.sync_service import SyncService
from backend.config import get_config


# Pydantic models for API
class DownloadResponse(BaseModel):
    id: str
    name: str
    status: str
    progress: float
    size_total: float | None
    size_left: float | None
    time_left: str | None
    speed: float | None
    category: str | None
    priority: str | None
    media_type: str | None
    media_title: str | None
    poster_url: str | None
    year: int | None
    arr_instance: str | None
    added_at: str
    completed_at: str | None
    failed: bool
    failure_reason: str | None

    class Config:
        from_attributes = True


class PriorityUpdate(BaseModel):
    priority: str  # force, high, normal, low, paused


# Global scheduler
scheduler = AsyncIOScheduler()
sync_service = SyncService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    config = get_config()
    await db.init_db()

    # Initial sync
    await sync_service.sync_downloads()

    # Schedule periodic syncs
    scheduler.add_job(sync_service.sync_downloads, 'interval', seconds=5, id='sync_downloads')
    scheduler.add_job(
        sync_service.cleanup_completed,
        'interval',
        minutes=config.cleanup.check_interval_minutes,
        id='cleanup_completed'
    )
    scheduler.start()

    print(f"✅ SABnzbd Media Tracker started")
    print(f"📊 Real-time sync: Every 5 seconds")
    print(f"🧹 Cleanup: Every {config.cleanup.check_interval_minutes} minutes (removing items older than {config.cleanup.completed_after_hours}h)")

    yield

    # Shutdown
    scheduler.shutdown()


app = FastAPI(title="SABnzbd Media Tracker", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def get_db_session():
    """Dependency to get database session."""
    async for session in db.get_session():
        yield session


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "SABnzbd Media Tracker API"}


@app.get("/api/downloads", response_model=List[DownloadResponse])
async def get_all_downloads(session: AsyncSession = Depends(get_db_session)):
    """Get all downloads."""
    downloads = await sync_service.get_all_downloads(session)
    return [
        DownloadResponse(
            id=d.id,
            name=d.name,
            status=d.status,
            progress=d.progress or 0.0,
            size_total=d.size_total,
            size_left=d.size_left,
            time_left=d.time_left,
            speed=d.speed,
            category=d.category,
            priority=d.priority,
            media_type=d.media_type,
            media_title=d.media_title,
            poster_url=d.poster_url,
            year=d.year,
            arr_instance=d.arr_instance,
            added_at=d.added_at.isoformat() if d.added_at else None,
            completed_at=d.completed_at.isoformat() if d.completed_at else None,
            failed=d.failed or False,
            failure_reason=d.failure_reason
        )
        for d in downloads
    ]


@app.get("/api/downloads/downloading", response_model=List[DownloadResponse])
async def get_downloading(session: AsyncSession = Depends(get_db_session)):
    """Get currently downloading items (including processing/unpacking)."""
    downloads = await sync_service.get_downloads_by_status(session, "downloading")
    return [DownloadResponse.from_orm(d) for d in downloads]


@app.get("/api/downloads/queued", response_model=List[DownloadResponse])
async def get_queued(session: AsyncSession = Depends(get_db_session)):
    """Get queued items."""
    downloads = await sync_service.get_downloads_by_status(session, "queued")
    return [DownloadResponse.from_orm(d) for d in downloads]


@app.get("/api/downloads/completed", response_model=List[DownloadResponse])
async def get_completed(session: AsyncSession = Depends(get_db_session)):
    """Get completed items."""
    downloads = await sync_service.get_downloads_by_status(session, "completed")
    return [DownloadResponse.from_orm(d) for d in downloads]


@app.get("/api/downloads/failed", response_model=List[DownloadResponse])
async def get_failed(session: AsyncSession = Depends(get_db_session)):
    """Get failed downloads."""
    downloads = await sync_service.get_downloads_by_status(session, "failed")
    return [DownloadResponse.from_orm(d) for d in downloads]


@app.post("/api/downloads/{download_id}/priority")
async def update_download_priority(download_id: str, priority_update: PriorityUpdate):
    """Update download priority."""
    success = await sync_service.update_priority(download_id, priority_update.priority)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update priority")

    return {"status": "ok", "message": "Priority updated"}


@app.get("/api/stats")
async def get_stats(session: AsyncSession = Depends(get_db_session)):
    """Get statistics about downloads."""
    all_downloads = await sync_service.get_all_downloads(session)

    downloading = len([d for d in all_downloads if d.status == "downloading"])
    queued = len([d for d in all_downloads if d.status == "queued"])
    completed = len([d for d in all_downloads if d.status == "completed"])
    failed = len([d for d in all_downloads if d.failed])

    # Calculate total speed
    total_speed = sum(d.speed or 0 for d in all_downloads if d.status == "downloading")

    return {
        "downloading": downloading,
        "queued": queued,
        "completed": completed,
        "failed": failed,
        "total_speed": round(total_speed, 2)
    }


if __name__ == "__main__":
    config = get_config()
    uvicorn.run(
        "backend.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=True
    )
