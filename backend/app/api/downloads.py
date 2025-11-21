"""
Download API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from backend.app.database import db
from backend.app.schemas import DownloadResponse, PriorityUpdate
from backend.app.models import Download

# Import will be provided by main.py
sync_service = None

router = APIRouter(prefix="/api/downloads", tags=["downloads"])


async def get_db_session():
    """Dependency to get database session."""
    async for session in db.get_session():
        yield session


@router.get("", response_model=List[DownloadResponse])
async def get_all_downloads(session: AsyncSession = Depends(get_db_session)):
    """Get all downloads."""
    downloads = await sync_service.get_all_downloads(session)
    return [DownloadResponse.model_validate(d) for d in downloads]


@router.get("/downloading", response_model=List[DownloadResponse])
async def get_downloading(session: AsyncSession = Depends(get_db_session)):
    """Get currently downloading items."""
    downloads = await sync_service.get_downloads_by_status(session, "downloading")
    return [DownloadResponse.model_validate(d) for d in downloads]


@router.get("/queued", response_model=List[DownloadResponse])
async def get_queued(session: AsyncSession = Depends(get_db_session)):
    """Get queued items."""
    downloads = await sync_service.get_downloads_by_status(session, "queued")
    return [DownloadResponse.model_validate(d) for d in downloads]


@router.get("/completed", response_model=List[DownloadResponse])
async def get_completed(session: AsyncSession = Depends(get_db_session)):
    """Get completed items."""
    downloads = await sync_service.get_downloads_by_status(session, "completed")
    return [DownloadResponse.model_validate(d) for d in downloads]


@router.get("/failed", response_model=List[DownloadResponse])
async def get_failed(session: AsyncSession = Depends(get_db_session)):
    """Get failed downloads."""
    downloads = await sync_service.get_downloads_by_status(session, "failed")
    return [DownloadResponse.model_validate(d) for d in downloads]


@router.post("/{download_id}/priority")
async def update_download_priority(download_id: str, priority_update: PriorityUpdate):
    """Update download priority."""
    success = await sync_service.update_priority(download_id, priority_update.priority)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update priority")

    return {"status": "ok", "message": "Priority updated"}


@router.post("/admin/reset-poster-flags")
async def reset_poster_flags(session: AsyncSession = Depends(get_db_session)):
    """Reset poster_attempted flag for items without posters."""
    try:
        from sqlalchemy import update

        result = await session.execute(
            update(Download)
            .where(Download.poster_url == None)
            .where(Download.poster_attempted == True)
            .values(poster_attempted=False)
        )

        await session.commit()
        count = result.rowcount

        return {
            "status": "ok",
            "message": f"Reset poster_attempted for {count} items"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset flags: {str(e)}")
