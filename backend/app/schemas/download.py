"""
Pydantic schemas for download data validation.
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class DownloadResponse(BaseModel):
    """Schema for download API responses."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    detailed_status: Optional[str] = None
    progress: float = 0.0
    size_total: Optional[float] = None
    size_left: Optional[float] = None
    time_left: Optional[str] = None
    speed: Optional[float] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    queue_position: Optional[int] = None
    media_type: Optional[str] = None
    media_title: Optional[str] = None
    poster_url: Optional[str] = None
    year: Optional[int] = None
    arr_instance: Optional[str] = None
    season: Optional[int] = None
    episode: Optional[int] = None
    added_at: datetime
    completed_at: Optional[datetime] = None
    failed: bool = False
    failure_reason: Optional[str] = None


class PriorityUpdate(BaseModel):
    """Schema for priority update requests."""

    priority: str = Field(
        ...,
        description="Priority level: force, high, normal, or low",
        pattern="^(force|high|normal|low)$"
    )


class StatsResponse(BaseModel):
    """Schema for statistics API response."""

    downloading: int = 0
    queued: int = 0
    completed: int = 0
    failed: int = 0
    total_speed: float = 0.0
