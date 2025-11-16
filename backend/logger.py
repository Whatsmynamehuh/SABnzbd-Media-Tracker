"""
Enhanced logging system for SABnzbd Media Tracker.
Provides beautiful, informative logs with progress tracking.
"""
from datetime import datetime
from typing import List, Dict, Optional
import math


class Logger:
    """Enhanced logger with smart formatting and progress tracking."""

    def __init__(self):
        self.last_sync_state = None
        self.last_download_progress = {}
        self.poster_fetch_start_time = None
        self.total_posters_needed = 0
        self.milestones_hit = set()
        self.errors_buffer = []
        self.last_error_report = datetime.now()

    def timestamp(self) -> str:
        """Get formatted timestamp."""
        return f"[{datetime.now().strftime('%H:%M:%S')}]"

    def draw_box(self, title: str, width: int = 78) -> None:
        """Draw a box around text."""
        print("╔" + "═" * (width - 2) + "╗")
        padding = (width - 2 - len(title)) // 2
        print("║" + " " * padding + title + " " * (width - 2 - padding - len(title)) + "║")
        print("╚" + "═" * (width - 2) + "╝")

    def separator(self, width: int = 80) -> None:
        """Print a separator line."""
        print("-" * width)

    def progress_bar(self, current: int, total: int, width: int = 30, fill: str = "█", empty: str = "░") -> str:
        """Generate ASCII progress bar."""
        if total == 0:
            return f"[{empty * width}]"

        percent = current / total
        filled = int(width * percent)
        bar = fill * filled + empty * (width - filled)
        return f"[{bar}]"

    def startup_banner(self, config) -> None:
        """Print startup banner with connection info."""
        print("=" * 80)
        print("SABnzbd Media Tracker v1.0 - STARTED")
        print("=" * 80)
        print()
        print(f"{self.timestamp()} Connected to SABnzbd: {config.sabnzbd.url}")

        for radarr in config.radarr:
            print(f"{self.timestamp()} Connected to Radarr: {radarr.name}")

        for sonarr in config.sonarr:
            print(f"{self.timestamp()} Connected to Sonarr: {sonarr.name}")

        print()
        print(f"{self.timestamp()} Sync Interval: 5s | Poster Fetch: 10s | Cleanup: {config.cleanup.completed_after_hours}h retention")
        print()

    def initial_sync(self, downloading: int, queued: int, completed: int, active_download: Optional[Dict] = None) -> None:
        """Log initial sync results."""
        total = downloading + queued + completed

        if active_download:
            name = active_download.get('media_title') or active_download.get('name', 'Unknown')
            progress = active_download.get('progress', 0)
            print(f"{self.timestamp()} Initial sync complete - Downloading: {downloading} ({name} - {progress:.1f}%), Queued: {queued}, Completed: {completed}, Total: {total}")
        else:
            print(f"{self.timestamp()} Initial sync complete - Downloading: {downloading}, Queued: {queued}, Completed: {completed}, Total: {total}")
        print()

        # Store state
        self.last_sync_state = {
            'downloading': downloading,
            'queued': queued,
            'completed': completed,
            'total': total
        }

    def sync_change(self, downloading: int, queued: int, completed: int, change_desc: Optional[str] = None) -> None:
        """Log only when sync state changes."""
        current_state = {
            'downloading': downloading,
            'queued': queued,
            'completed': completed,
            'total': downloading + queued + completed
        }

        # Only log if something changed
        if self.last_sync_state and current_state != self.last_sync_state:
            if change_desc:
                print(f"{self.timestamp()} Queue update - {change_desc} - Downloading: {downloading}, Queued: {queued}, Completed: {completed}")
            else:
                print(f"{self.timestamp()} Queue update - Downloading: {downloading}, Queued: {queued}, Completed: {completed}")

            self.last_sync_state = current_state

    def download_progress(self, download: Dict) -> None:
        """Log download progress changes (only significant changes)."""
        download_id = download.get('id')
        current_progress = download.get('progress', 0)
        name = download.get('media_title') or download.get('name', 'Unknown')
        speed = download.get('speed', 0)
        time_left = download.get('time_left', 'Unknown')

        # Only log if progress changed by 5% or more
        last_progress = self.last_download_progress.get(download_id, 0)
        if abs(current_progress - last_progress) >= 5:
            print(f"{self.timestamp()} 📊 Download Progress")
            print(f"           └─ {name[:50]}: {last_progress:.0f}% → {current_progress:.0f}% (+{current_progress - last_progress:.0f}%) @ {speed:.1f} MB/s")
            if time_left and time_left != 'Unknown':
                print(f"              ⏱️  {time_left} remaining")
            print()

            self.last_download_progress[download_id] = current_progress

    def download_complete(self, download: Dict) -> None:
        """Log download completion with celebration."""
        name = download.get('media_title') or download.get('name', 'Unknown')
        size = download.get('size_total', 0)

        print(f"{self.timestamp()} ✅ DOWNLOAD COMPLETE!")
        self.draw_box(f"  {name[:50]}")

        if size > 1024:
            print(f"           └─ Size: {size / 1024:.1f} GB")
        else:
            print(f"           └─ Size: {size:.1f} MB")

        print(f"              Moving to: Completed section")
        print()

        # Clear from progress tracking
        download_id = download.get('id')
        if download_id in self.last_download_progress:
            del self.last_download_progress[download_id]

    def poster_fetch_start(self, fetch_type: str, downloading_remaining: int, completed_remaining: int, queued_remaining: int) -> None:
        """Log start of poster fetch batch."""
        total = downloading_remaining + completed_remaining + queued_remaining

        if self.poster_fetch_start_time is None:
            self.poster_fetch_start_time = datetime.now()
            self.total_posters_needed = total

        if fetch_type == "downloading":
            print(f"{self.timestamp()} 🖼️  Poster Fetch: Downloading (Priority 1)")
            if completed_remaining > 0 or queued_remaining > 0:
                print(f"           └─ {completed_remaining} completed + {queued_remaining} queued remaining")
        elif fetch_type == "completed":
            print(f"{self.timestamp()} 🖼️  Poster Fetch: Completed Items (Priority 2)")
            if queued_remaining > 0:
                print(f"           └─ {completed_remaining} completed + {queued_remaining} queued remaining")
        elif fetch_type == "queued":
            print(f"{self.timestamp()} 🖼️  Poster Fetch: Queue (Priority 3)")
            print(f"           └─ Fetching by position (#2, #3, #4...)")

    def poster_fetch_results(self, found: List[str], not_found: List[str], total_found: int, total_needed: int) -> None:
        """Log poster fetch results with progress."""
        # Show found items (limit to 5)
        for i, item in enumerate(found[:5]):
            prefix = "├─" if i < len(found[:5]) - 1 or len(not_found) > 0 else "└─"
            print(f"           {prefix} ✓ {item}")

        if len(found) > 5:
            print(f"           ├─ ... and {len(found) - 5} more")

        # Show not found items (limit to 3)
        for i, item in enumerate(not_found[:3]):
            prefix = "└─" if i == len(not_found[:3]) - 1 else "├─"
            print(f"           {prefix} ✗ Not found: {item}")

        # Batch summary
        batch_size = len(found) + len(not_found)
        success_rate = (len(found) / batch_size * 100) if batch_size > 0 else 0
        print(f"           └─ Batch: {len(found)}/{batch_size} found ({success_rate:.0f}% success)")
        print()

        # Progress bar
        percent = (total_found / total_needed * 100) if total_needed > 0 else 0
        bar = self.progress_bar(total_found, total_needed, width=30)
        print(f"           Progress: {bar} {total_found}/{total_needed} ({percent:.1f}%)")

        # Calculate ETA
        if self.poster_fetch_start_time and total_found > 0:
            elapsed = (datetime.now() - self.poster_fetch_start_time).total_seconds()
            rate = total_found / elapsed * 60  # posters per minute
            remaining = total_needed - total_found
            eta_minutes = remaining / rate if rate > 0 else 0

            if eta_minutes > 60:
                print(f"           ETA: ~{eta_minutes / 60:.0f}h {eta_minutes % 60:.0f}m @ {rate:.0f} posters/min")
            else:
                print(f"           ETA: ~{eta_minutes:.0f}m @ {rate:.0f} posters/min")

        print()

        # Check for milestones
        self.check_milestone(total_found, total_needed)

    def check_milestone(self, current: int, total: int) -> None:
        """Check and log milestone achievements."""
        if total == 0:
            return

        percent = (current / total) * 100
        milestones = [25, 50, 75, 100]

        for milestone in milestones:
            if percent >= milestone and milestone not in self.milestones_hit:
                self.milestones_hit.add(milestone)

                if milestone == 100:
                    self.poster_complete(current, total)
                else:
                    elapsed = (datetime.now() - self.poster_fetch_start_time).total_seconds() / 60
                    rate = current / elapsed if elapsed > 0 else 0
                    remaining = total - current
                    eta = remaining / rate if rate > 0 else 0

                    print(f"{self.timestamp()} 🎯 MILESTONE: {milestone}% Complete")
                    print(f"           ├─ Posters fetched: {current}/{total}")
                    if milestone < 100:
                        print(f"           ├─ Time elapsed: {elapsed:.0f}m | ETA: {eta:.0f}m")
                        print(f"           └─ Speed: {rate:.0f} posters/min")
                    print()

    def poster_complete(self, total_found: int, total_needed: int) -> None:
        """Log poster fetching completion."""
        elapsed = (datetime.now() - self.poster_fetch_start_time).total_seconds() / 60
        rate = total_found / elapsed if elapsed > 0 else 0
        success_rate = (total_found / total_needed * 100) if total_needed > 0 else 0

        print(f"{self.timestamp()} 🎉 ALL POSTERS COMPLETE!")
        self.draw_box("  ✨ Poster fetching finished!")
        print(f"           ├─ Total: {total_needed} items processed")
        print(f"           ├─ Found: {total_found} posters ({success_rate:.0f}% success)")

        if total_needed - total_found > 0:
            print(f"           ├─ Failed: {total_needed - total_found} items (not in Radarr/Sonarr)")

        print(f"           ├─ Duration: {elapsed:.0f}m")
        print(f"           └─ Average: {rate:.0f} posters/minute")
        print()
        print("           All posters loaded! Now monitoring for new downloads...")
        print()

        # Reset for next batch
        self.poster_fetch_start_time = None
        self.milestones_hit.clear()

    def error(self, message: str, context: Optional[str] = None) -> None:
        """Log an error with optional context."""
        error_entry = {
            'time': datetime.now(),
            'message': message,
            'context': context
        }
        self.errors_buffer.append(error_entry)

        # If we have 5+ errors, show summary
        if len(self.errors_buffer) >= 5:
            self.error_summary()

    def error_summary(self) -> None:
        """Show aggregated error summary."""
        if not self.errors_buffer:
            return

        # Group errors by message
        error_groups = {}
        for error in self.errors_buffer:
            msg = error['message']
            if msg not in error_groups:
                error_groups[msg] = []
            error_groups[msg].append(error)

        print(f"{self.timestamp()} ⚠️  ERRORS DETECTED (Last minute)")
        for msg, errors in error_groups.items():
            count = len(errors)
            contexts = [e.get('context') for e in errors if e.get('context')]
            if count > 1:
                print(f"           ├─ 🔴 {msg} ({count}x)")
            else:
                print(f"           ├─ 🔴 {msg}")

            if contexts:
                print(f"              └─ Affected: {', '.join(set(contexts[:3]))}")

        print(f"           └─ 💡 Suggestion: Check your Radarr/Sonarr instances")
        print()

        # Clear buffer
        self.errors_buffer.clear()
        self.last_error_report = datetime.now()

    def cleanup_start(self, total_items: int) -> None:
        """Log cleanup job start."""
        print(f"{self.timestamp()} Cleanup: Checking {total_items} completed items")

    def cleanup_complete(self, removed_items: List[str], kept_count: int) -> None:
        """Log cleanup results."""
        print(f"{self.timestamp()} Cleanup complete: {len(removed_items)} removed, {kept_count} kept (within retention period)")
        for item in removed_items:
            print(f"{self.timestamp()}   Removed: {item}")
        print()


# Global logger instance
logger = Logger()
