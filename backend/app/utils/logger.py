"""
Enhanced logging system for SABnzbd Media Tracker.
"""
from datetime import datetime
from typing import List, Dict, Optional


class Logger:
    """Enhanced logger with beautiful formatting."""

    def __init__(self):
        """Initialize logger."""
        self.last_sync_state = None

    def timestamp(self) -> str:
        """Get formatted timestamp."""
        return f"[{datetime.now().strftime('%H:%M:%S')}]"

    def separator(self, width: int = 80) -> None:
        """Print a separator line."""
        print("-" * width)

    def startup_banner(self, config) -> None:
        """Print startup banner."""
        print("=" * 80)
        print("SABnzbd Media Tracker v2.0 - STARTED")
        print("=" * 80)
        print()
        print(f"{self.timestamp()} Connected to SABnzbd: {config.sabnzbd.url}")

        for radarr in config.radarr:
            print(f"{self.timestamp()} Connected to Radarr: {radarr.name} (category: {radarr.category})")

        for sonarr in config.sonarr:
            print(f"{self.timestamp()} Connected to Sonarr: {sonarr.name} (category: {sonarr.category})")

        print()
        print(f"{self.timestamp()} Sync: 5s | Poster: 10s | Cleanup: {config.cleanup.completed_after_hours}h retention")
        print()

    def initial_sync(
        self,
        downloading: int,
        queued: int,
        completed: int,
        active_download: Optional[Dict] = None
    ) -> None:
        """Log initial sync results."""
        total = downloading + queued + completed

        if active_download:
            name = active_download.get('media_title') or active_download.get('name', 'Unknown')
            progress = active_download.get('progress', 0)
            print(f"{self.timestamp()} Initial sync - Downloading: {downloading} ({name[:50]} - {progress:.1f}%), Queued: {queued}, Completed: {completed}")
        else:
            print(f"{self.timestamp()} Initial sync - Downloading: {downloading}, Queued: {queued}, Completed: {completed}")

        print()

        self.last_sync_state = {
            'downloading': downloading,
            'queued': queued,
            'completed': completed,
            'total': total
        }

    def sync_change(self, downloading: int, queued: int, completed: int) -> None:
        """Log sync state changes."""
        current_state = {
            'downloading': downloading,
            'queued': queued,
            'completed': completed,
            'total': downloading + queued + completed
        }

        # Only log if something changed
        if self.last_sync_state and current_state != self.last_sync_state:
            print(f"{self.timestamp()} Queue update - Downloading: {downloading}, Queued: {queued}, Completed: {completed}")
            self.last_sync_state = current_state

    def cleanup_start(self, total_items: int) -> None:
        """Log cleanup start."""
        print(f"{self.timestamp()} 🧹 Cleanup: Checking {total_items} completed/failed items")

    def cleanup_complete(self, removed_items: List[str], kept_count: int) -> None:
        """Log cleanup complete."""
        print(f"{self.timestamp()} 🧹 Cleanup: {len(removed_items)} removed, {kept_count} kept")
        for item in removed_items[:10]:  # Show first 10
            print(f"{self.timestamp()}   {item}")
        if len(removed_items) > 10:
            print(f"{self.timestamp()}   ... and {len(removed_items) - 10} more")
        print()


# Global logger instance
logger = Logger()
