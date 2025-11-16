import asyncio
import aiohttp
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import Download, db
from backend.sabnzbd_client import SABnzbdClient
from backend.arr_client import ArrManager
from backend.config import get_config
from typing import List, Dict, Any


class SyncService:
    """Service to sync data between SABnzbd, Radarr/Sonarr and local database."""

    def __init__(self):
        config = get_config()
        self.sabnzbd = SABnzbdClient(config.sabnzbd.url, config.sabnzbd.api_key)

        # Initialize Arr manager
        radarr_configs = [r.dict() for r in config.radarr]
        sonarr_configs = [s.dict() for s in config.sonarr]
        self.arr_manager = ArrManager(radarr_configs, sonarr_configs)

        self.cleanup_hours = config.cleanup.completed_after_hours

    async def sync_downloads(self, fetch_media_info: bool = True):
        """Sync downloads from SABnzbd to database."""
        try:
            # Get queue and history from SABnzbd
            queue_data = await self.sabnzbd.get_queue()
            history_data = await self.sabnzbd.get_history()

            # Parse items
            queue_items = self.sabnzbd.parse_queue_items(queue_data)
            history_items = self.sabnzbd.parse_history_items(history_data)

            all_items = queue_items + history_items

            if not all_items:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  No items from SABnzbd")
                return

            # Update database
            async for session in db.get_session():
                for item in all_items:
                    await self._update_or_create_download(session, item, fetch_media_info)

                await session.commit()

            # Show stats
            downloading_count = len([i for i in queue_items if i.get('status') == 'downloading'])
            queued_count = len([i for i in queue_items if i.get('status') == 'queued'])
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Synced {len(all_items)} downloads (Downloading: {downloading_count}, Queued: {queued_count}, History: {len(history_items)})")

        except aiohttp.ClientConnectorError as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Cannot connect to SABnzbd - check if it's running and config.yml is correct")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error syncing downloads: {e}")

    async def _update_or_create_download(self, session: AsyncSession, item: Dict[str, Any], fetch_media_info: bool = True):
        """Update or create a download record."""
        # Check if download exists
        result = await session.execute(
            select(Download).where(Download.id == item["id"])
        )
        download = result.scalar_one_or_none()

        if download:
            # Update existing
            for key, value in item.items():
                if hasattr(download, key):
                    setattr(download, key, value)

            download.updated_at = datetime.utcnow()

            # Don't fetch media info for existing items during regular sync
            # A separate background job will handle this
            pass
        else:
            # Create new
            download = Download(id=item["id"])
            for key, value in item.items():
                if hasattr(download, key):
                    setattr(download, key, value)

            # Mark for media info fetch (will be done by background job)
            session.add(download)

    async def cleanup_completed(self):
        """Remove completed downloads older than configured hours."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_hours)

            async for session in db.get_session():
                result = await session.execute(
                    delete(Download).where(
                        Download.status == "completed",
                        Download.completed_at < cutoff_time
                    )
                )

                await session.commit()

                deleted_count = result.rowcount
                if deleted_count > 0:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🗑️  Cleaned up {deleted_count} completed downloads (older than {self.cleanup_hours}h)")

        except Exception as e:
            print(f"Error cleaning up completed downloads: {e}")

    async def get_all_downloads(self, session: AsyncSession) -> List[Download]:
        """Get all downloads from database."""
        result = await session.execute(select(Download))
        return result.scalars().all()

    async def get_downloads_by_status(self, session: AsyncSession, status: str) -> List[Download]:
        """Get downloads by status."""
        result = await session.execute(
            select(Download).where(Download.status == status)
        )
        return result.scalars().all()

    async def fetch_missing_media_info(self):
        """Fetch media info for downloads that don't have it yet (batched, prioritized)."""
        try:
            async for session in db.get_session():
                # Count total active items without posters
                active_result = await session.execute(
                    select(Download)
                    .where(Download.poster_url == None)
                    .where(Download.status.in_(['downloading', 'queued']))
                )
                active_without = len(active_result.scalars().all())

                # Count total completed items without posters
                completed_result = await session.execute(
                    select(Download)
                    .where(Download.poster_url == None)
                    .where(Download.status == 'completed')
                )
                completed_without = len(completed_result.scalars().all())

                total_without = active_without + completed_without

                if total_without == 0:
                    return

                # Priority 1: Downloading items first
                # Priority 2: Queued items (ordered by queue position #1, #2, #3...)
                # Priority 3: Completed items (after queue is done)
                if active_without > 0:
                    # Fetch active/queued items first, ordered by position
                    result = await session.execute(
                        select(Download)
                        .where(Download.poster_url == None)
                        .where(Download.status.in_(['downloading', 'queued']))
                        .order_by(
                            Download.status.desc(),  # downloading before queued
                            Download.queue_position.asc()  # then by position #1, #2, #3...
                        )
                        .limit(20)
                    )
                    downloads_without_info = result.scalars().all()
                    fetch_type = "queue"
                else:
                    # All queue items have posters, now fetch completed items
                    result = await session.execute(
                        select(Download)
                        .where(Download.poster_url == None)
                        .where(Download.status == 'completed')
                        .order_by(Download.completed_at.desc())  # newest first
                        .limit(20)
                    )
                    downloads_without_info = result.scalars().all()
                    fetch_type = "completed"

                if not downloads_without_info:
                    return

                if fetch_type == "queue":
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🖼️  Fetching posters for queue (priority order)... ({active_without} active + {completed_without} completed remaining)")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🖼️  Queue done! Fetching posters for completed items... ({completed_without} remaining)")

                found_count = 0
                for download in downloads_without_info:
                    try:
                        media_info = await self.arr_manager.search_all(download.name)
                        if media_info:
                            download.media_type = media_info.get("media_type")
                            download.media_title = media_info.get("media_title")
                            download.poster_url = media_info.get("poster_url")
                            download.year = media_info.get("year")
                            download.arr_instance = media_info.get("arr_instance")
                            found_count += 1
                    except Exception as e:
                        print(f"  ✗ Error: {str(e)[:80]}")
                        continue

                await session.commit()

                # Calculate totals for progress display
                if fetch_type == "queue":
                    total_items = active_without + completed_without
                    found_so_far = total_items - (active_without - found_count) - completed_without
                    print(f"  ✓ Found {found_count}/{len(downloads_without_info)} • Progress: {found_so_far}/{total_items} posters")
                else:
                    remaining = completed_without - found_count
                    print(f"  ✓ Found {found_count}/{len(downloads_without_info)} • {remaining} completed items still need posters")

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error fetching media info: {e}")

    async def update_priority(self, download_id: str, priority: str) -> bool:
        """Update download priority in SABnzbd."""
        try:
            # Map priority names to SABnzbd values
            priority_map = {
                "force": 3,
                "high": 2,
                "normal": 1,
                "low": 0,
                "paused": -1
            }

            priority_value = priority_map.get(priority.lower(), 1)
            await self.sabnzbd.set_priority(download_id, priority_value)

            # Update in database
            async for session in db.get_session():
                result = await session.execute(
                    select(Download).where(Download.id == download_id)
                )
                download = result.scalar_one_or_none()

                if download:
                    download.priority = priority
                    await session.commit()

            return True
        except Exception as e:
            print(f"Error updating priority: {e}")
            return False
