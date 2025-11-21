"""
Download model for tracking SABnzbd downloads.
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, Text
from backend.app.database import Base


class Download(Base):
    """Model for tracking downloads from SABnzbd."""

    __tablename__ = "downloads"

    # Primary key
    id = Column(String, primary_key=True)  # SABnzbd NZO ID

    # Download info
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # downloading, queued, completed, failed
    detailed_status = Column(String, nullable=True)  # SABnzbd status (Downloading, Extracting, etc.)
    progress = Column(Float, default=0.0)  # 0-100
    size_total = Column(Float, nullable=True)  # in MB
    size_left = Column(Float, nullable=True)  # in MB
    time_left = Column(String, nullable=True)
    speed = Column(Float, nullable=True)  # MB/s
    category = Column(String, nullable=True)
    priority = Column(String, nullable=True)  # Force, High, Normal, Low
    queue_position = Column(Integer, nullable=True)  # Position in queue

    # Media info from Radarr/Sonarr
    media_type = Column(String, nullable=True)  # movie or tv
    media_title = Column(String, nullable=True)
    poster_url = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    arr_instance = Column(String, nullable=True)  # Which Radarr/Sonarr instance
    poster_attempted = Column(Boolean, default=False)  # Have we tried fetching poster?

    # TV Show episode info (for media_type='tv')
    # NOTE: These are integers or None - NEVER lists!
    season = Column(Integer, nullable=True)  # Season number
    episode = Column(Integer, nullable=True)  # Episode number

    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Failed downloads
    failed = Column(Boolean, default=False, nullable=False)
    failure_reason = Column(Text, nullable=True)

    def __repr__(self) -> str:
        """String representation."""
        return f"<Download(id='{self.id}', name='{self.name}', status='{self.status}')>"
