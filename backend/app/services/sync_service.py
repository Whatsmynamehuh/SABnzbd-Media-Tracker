"""
Sync service to sync data between SABnzbd, Radarr/Sonarr and local database.
"""
import asyncio
import aiohttp
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models import Download
from backend.app.database import db
from backend.app.services.sabnzbd_client import SABnzbdClient
from backend.app.services.arr_client import ArrManager
from backend.app.utils.logger import logger
from typing import List, Dict, Any


class SyncService:
    """Service to sync downloads from SABnzbd and fetch media info from Arr."""

    def __init__(self, config):
        """
        Initialize sync service.

        Args:
            config: Application configuration
        """
        self.sabnzbd = SABnzbdClient(
            config.sabnzbd.url,
            config.sabnzbd.api_key,
            enable_priority_logging=config.debug.enable_priority_logging
        )

        # Initialize Arr manager
        radarr_configs = [r.model_dump() for r in config.radarr]
        sonarr_configs = [s.model_dump() for s in config.sonarr]
        self.arr_manager = ArrManager(
            radarr_configs,
            sonarr_configs,
            enable_category_logging=config.debug.enable_category_logging,
            enable_parsing_logging=config.debug.enable_parsing_logging,
            enable_match_logging=config.debug.enable_match_logging,
            enable_poster_logging=config.debug.enable_poster_logging
        )

        self.cleanup_hours = config.cleanup.completed_after_hours

    async def sync_downloads(self, fetch_media_info: bool = True, is_initial: bool = False) -> None:
        """
        Sync downloads from SABnzbd to database.

        Args:
            fetch_media_info: Whether to fetch media info (poster, etc.)
            is_initial: Whether this is the initial sync on startup
        """
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

                # Clean up orphaned downloads
                await self._cleanup_orphaned_downloads(session, all_items)

                await session.commit()

            # Calculate stats
            downloading_count = len([i for i in queue_items if i.get('status') == 'downloading'])
            queued_count = len([i for i in queue_items if i.get('status') == 'queued'])
            completed_count = len([i for i in history_items if not i.get('failed')])

            # Log based on context
            if is_initial:
                active_download = next((i for i in queue_items if i.get('status') == 'downloading'), None)
                logger.initial_sync(downloading_count, queued_count, completed_count, active_download)
            else:
                logger.sync_change(downloading_count, queued_count, completed_count)

        except aiohttp.ClientConnectorError:
            print(f"{logger.timestamp()} ⚠️  Cannot connect to SABnzbd - check if it's running")
        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error syncing downloads: {e}")
            import traceback
            traceback.print_exc()

    async def _update_or_create_download(
        self,
        session: AsyncSession,
        item: Dict[str, Any],
        fetch_media_info: bool = True
    ) -> None:
        """
        Update or create a download record.

        Args:
            session: Database session
            item: Download item dict
            fetch_media_info: Whether to fetch media info
        """
        # Check if download exists
        result = await session.execute(
            select(Download).where(Download.id == item["id"])
        )
        download = result.scalar_one_or_none()

        if download:
            # Once completed/failed, freeze it (let cleanup handle removal)
            if download.status in ['completed', 'failed']:
                return

            # Update active downloads
            for key, value in item.items():
                if hasattr(download, key):
                    setattr(download, key, value)

            download.updated_at = datetime.utcnow()

            # Mark as completed if this update changes status
            if item.get('status') == 'completed' and not download.completed_at:
                download.completed_at = datetime.utcnow()

        else:
            # Create new download
            download = Download(id=item["id"])
            for key, value in item.items():
                if hasattr(download, key):
                    setattr(download, key, value)

            # Set completed_at for completed items
            if item.get('status') == 'completed':
                if item.get('completed_at'):
                    download.completed_at = item['completed_at']
                else:
                    download.completed_at = datetime.utcnow()

            session.add(download)

    async def _cleanup_orphaned_downloads(
        self,
        session: AsyncSession,
        current_items: List[Dict[str, Any]]
    ) -> None:
        """
        Remove downloads that are no longer in SABnzbd.

        Args:
            session: Database session
            current_items: Current items from SABnzbd
        """
        sabnzbd_ids = {item['id'] for item in current_items}

        # Get all active downloads from database
        result = await session.execute(
            select(Download).where(Download.status.in_(['downloading', 'queued']))
        )
        db_downloads = result.scalars().all()

        # Find orphaned downloads
        for download in db_downloads:
            if download.id not in sabnzbd_ids:
                download.status = 'failed'
                download.failed = True
                download.failure_reason = 'Removed from SABnzbd (manually deleted)'
                download.completed_at = datetime.utcnow()
                download.updated_at = datetime.utcnow()
                print(f"{logger.timestamp()} 🗑️  Orphaned: {download.name}")

    async def cleanup_old_downloads(self) -> None:
        """
        CRITICAL FIX: Remove BOTH completed AND failed downloads older than configured hours.

        This fixes the bug where failed downloads were never cleaned up.
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=self.cleanup_hours)

            async for session in db.get_session():
                # Get items to delete (BOTH completed AND failed)
                to_delete_result = await session.execute(
                    select(Download).where(
                        Download.status.in_(["completed", "failed"]),  # CRITICAL FIX: Both statuses
                        Download.completed_at < cutoff_time
                    )
                )
                to_delete = to_delete_result.scalars().all()

                # Get total count of completed + failed
                all_old_result = await session.execute(
                    select(Download).where(Download.status.in_(["completed", "failed"]))
                )
                total_old = len(all_old_result.scalars().all())

                if len(to_delete) > 0:
                    logger.cleanup_start(total_old)

                    # Create list of removed items
                    removed_items = []
                    for item in to_delete:
                        hours_ago = (datetime.utcnow() - item.completed_at).total_seconds() / 3600
                        name = item.media_title or item.name
                        status = "✅" if item.status == "completed" else "❌"
                        removed_items.append(f"{status} {name[:40]} ({hours_ago:.0f}h ago)")

                    # Delete them
                    await session.execute(
                        delete(Download).where(
                            Download.status.in_(["completed", "failed"]),  # CRITICAL FIX: Both statuses
                            Download.completed_at < cutoff_time
                        )
                    )
                    await session.commit()

                    # Log results
                    kept_count = total_old - len(to_delete)
                    logger.cleanup_complete(removed_items, kept_count)

        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error during cleanup: {e}")
            import traceback
            traceback.print_exc()

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

    async def fetch_missing_media_info(self) -> None:
        """Fetch media info for downloads that don't have posters yet."""
        try:
            async for session in db.get_session():
                # Get items without posters (prioritized by status)
                for status in ['downloading', 'completed', 'queued']:
                    result = await session.execute(
                        select(Download)
                        .where(Download.poster_url == None)
                        .where(Download.poster_attempted == False)
                        .where(Download.status == status)
                        .limit(5)
                    )
                    downloads_without_info = result.scalars().all()

                    if downloads_without_info:
                        found_count = 0

                        for download in downloads_without_info:
                            download.poster_attempted = True

                            try:
                                media_info = await self.arr_manager.search_all(
                                    download.name,
                                    download.category
                                )
                                if media_info:
                                    download.media_type = media_info.get("media_type")
                                    download.media_title = media_info.get("media_title")
                                    download.poster_url = media_info.get("poster_url")
                                    download.year = media_info.get("year")
                                    download.arr_instance = media_info.get("arr_instance")
                                    found_count += 1
                            except Exception:
                                pass  # Already marked as attempted

                        await session.commit()

                        if found_count > 0:
                            print(f"{logger.timestamp()} 🖼️  Found {found_count} posters ({status})")

                        break  # Only fetch one batch per run

        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error fetching media info: {e}")

    async def update_priority(self, download_id: str, priority: str) -> bool:
        """
        Update download priority in SABnzbd.

        Args:
            download_id: SABnzbd download ID
            priority: Priority level (force, high, normal, low)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Map priority names to SABnzbd values
            priority_map = {
                "force": 2,
                "high": 1,
                "normal": 0,
                "low": -1,
            }

            priority_value = priority_map.get(priority.lower(), 0)

            print(f"{logger.timestamp()} Setting priority: {priority} ({priority_value})")

            result = await self.sabnzbd.set_priority(download_id, priority_value)

            # Update in database
            async for session in db.get_session():
                db_result = await session.execute(
                    select(Download).where(Download.id == download_id)
                )
                download = db_result.scalar_one_or_none()

                if download:
                    download.priority = str(priority_value)
                    await session.commit()

            return True

        except Exception as e:
            print(f"{logger.timestamp()} ❌ Error updating priority: {e}")
            return False
