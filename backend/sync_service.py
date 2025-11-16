import asyncio
import aiohttp
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import Download, db
from backend.sabnzbd_client import SABnzbdClient
from backend.arr_client import ArrManager
from backend.config import get_config
from backend.logger import logger
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

    async def sync_downloads(self, fetch_media_info: bool = True, is_initial: bool = False):
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
                print(f"{logger.timestamp()} ⚠️  No items from SABnzbd")
                return

            # Update database
            async for session in db.get_session():
                for item in all_items:
                    await self._update_or_create_download(session, item, fetch_media_info)

                await session.commit()

            # Calculate stats
            downloading_count = len([i for i in queue_items if i.get('status') == 'downloading'])
            queued_count = len([i for i in queue_items if i.get('status') == 'queued'])
            completed_count = len([i for i in history_items if not i.get('failed')])

            # Log based on context
            if is_initial:
                # Initial sync - show full details
                active_download = next((i for i in queue_items if i.get('status') == 'downloading'), None)
                logger.initial_sync(downloading_count, queued_count, completed_count, active_download)
            else:
                # Regular sync - only log changes
                logger.sync_change(downloading_count, queued_count, completed_count)

        except aiohttp.ClientConnectorError as e:
            print(f"{logger.timestamp()} ⚠️  Cannot connect to SABnzbd - check if it's running and config.yml is correct")
        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error syncing downloads: {e}")

    async def _update_or_create_download(self, session: AsyncSession, item: Dict[str, Any], fetch_media_info: bool = True):
        """Update or create a download record."""
        # Check if download exists
        result = await session.execute(
            select(Download).where(Download.id == item["id"])
        )
        download = result.scalar_one_or_none()

        if download:
            # CRITICAL: Once an item is completed or failed, freeze it!
            # Don't update from SABnzbd anymore - let it persist for 48h cleanup
            if download.status in ['completed', 'failed']:
                # Item already completed/failed - don't touch it
                # It will persist until cleanup job removes it (48h later)
                # This ensures "Recently Completed" shows items even if SABnzbd removes them
                return

            # Update active downloads (downloading/queued)
            for key, value in item.items():
                if hasattr(download, key):
                    setattr(download, key, value)

            download.updated_at = datetime.utcnow()

            # If this update marks it as completed, set completed_at timestamp
            if item.get('status') == 'completed' and not download.completed_at:
                download.completed_at = datetime.utcnow()

        else:
            # Create new
            download = Download(id=item["id"])
            for key, value in item.items():
                if hasattr(download, key):
                    setattr(download, key, value)

            # Set completed_at if this is a completed item from history
            if item.get('status') == 'completed' and item.get('completed_at'):
                download.completed_at = item['completed_at']
            elif item.get('status') == 'completed':
                download.completed_at = datetime.utcnow()

            # Mark for media info fetch (will be done by background job)
            session.add(download)

    async def cleanup_completed(self):
        """Remove completed downloads older than configured hours."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_hours)

            async for session in db.get_session():
                # First, get items that will be deleted
                to_delete_result = await session.execute(
                    select(Download).where(
                        Download.status == "completed",
                        Download.completed_at < cutoff_time
                    )
                )
                to_delete = to_delete_result.scalars().all()

                # Get total completed count
                all_completed_result = await session.execute(
                    select(Download).where(Download.status == "completed")
                )
                total_completed = len(all_completed_result.scalars().all())

                if len(to_delete) > 0:
                    logger.cleanup_start(total_completed)

                    # Create list of removed items with time info
                    removed_items = []
                    for item in to_delete:
                        hours_ago = (datetime.utcnow() - item.completed_at).total_seconds() / 3600
                        name = item.media_title or item.name
                        removed_items.append(f"{name[:40]} (completed {hours_ago:.0f}h ago)")

                    # Now delete them
                    await session.execute(
                        delete(Download).where(
                            Download.status == "completed",
                            Download.completed_at < cutoff_time
                        )
                    )
                    await session.commit()

                    # Log results
                    kept_count = total_completed - len(to_delete)
                    logger.cleanup_complete(removed_items, kept_count)

        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error during cleanup: {e}")

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
                # Count items without posters that we haven't tried yet
                downloading_result = await session.execute(
                    select(Download)
                    .where(Download.poster_url == None)
                    .where(Download.poster_attempted == False)
                    .where(Download.status == 'downloading')
                )
                downloading_without = len(downloading_result.scalars().all())

                completed_result = await session.execute(
                    select(Download)
                    .where(Download.poster_url == None)
                    .where(Download.poster_attempted == False)
                    .where(Download.status == 'completed')
                )
                completed_without = len(completed_result.scalars().all())

                queued_result = await session.execute(
                    select(Download)
                    .where(Download.poster_url == None)
                    .where(Download.poster_attempted == False)
                    .where(Download.status == 'queued')
                )
                queued_without = len(queued_result.scalars().all())

                total_without = downloading_without + completed_without + queued_without

                if total_without == 0:
                    return

                # PRIORITY ORDER:
                # 1. Downloading (#1) - most important, what's downloading NOW
                # 2. Recently completed - what just finished
                # 3. Queued (#2, #3, #4...) - fill in queue posters last

                if downloading_without > 0:
                    # Priority 1: Currently downloading item
                    result = await session.execute(
                        select(Download)
                        .where(Download.poster_url == None)
                        .where(Download.poster_attempted == False)
                        .where(Download.status == 'downloading')
                        .limit(20)
                    )
                    downloads_without_info = result.scalars().all()
                    fetch_type = "downloading"

                elif completed_without > 0:
                    # Priority 2: Recently completed items (newest first)
                    result = await session.execute(
                        select(Download)
                        .where(Download.poster_url == None)
                        .where(Download.poster_attempted == False)
                        .where(Download.status == 'completed')
                        .order_by(Download.completed_at.desc())  # newest first
                        .limit(20)
                    )
                    downloads_without_info = result.scalars().all()
                    fetch_type = "completed"

                elif queued_without > 0:
                    # Priority 3: Queued items (by position #2, #3, #4...)
                    result = await session.execute(
                        select(Download)
                        .where(Download.poster_url == None)
                        .where(Download.poster_attempted == False)
                        .where(Download.status == 'queued')
                        .order_by(Download.queue_position.asc())  # #2, #3, #4...
                        .limit(20)
                    )
                    downloads_without_info = result.scalars().all()
                    fetch_type = "queued"

                else:
                    return

                if not downloads_without_info:
                    return

                # Fetch posters
                found_count = 0

                for download in downloads_without_info:
                    # Mark as attempted (whether we find it or not)
                    download.poster_attempted = True

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
                        pass  # Already marked as attempted

                await session.commit()

                # Simple log output
                if found_count > 0:
                    remaining = downloading_without + completed_without + queued_without - len(downloads_without_info)
                    print(f"{logger.timestamp()} 🖼️  Found {found_count} posters ({fetch_type}) • {remaining} remaining")

        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error fetching media info: {e}")

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

            print(f"{logger.timestamp()} Setting priority for {download_id}: {priority} -> {priority_value}")

            result = await self.sabnzbd.set_priority(download_id, priority_value)
            print(f"{logger.timestamp()} SABnzbd response: {result}")

            # Update in database
            async for session in db.get_session():
                db_result = await session.execute(
                    select(Download).where(Download.id == download_id)
                )
                download = db_result.scalar_one_or_none()

                if download:
                    download.priority = str(priority_value)  # Store numeric value
                    await session.commit()
                    print(f"{logger.timestamp()} Updated priority in database")
                else:
                    print(f"{logger.timestamp()} Warning: Download {download_id} not found in database")

            return True
        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error updating priority: {e}")
            import traceback
            traceback.print_exc()
            return False
