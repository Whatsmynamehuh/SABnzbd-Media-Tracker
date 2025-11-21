"""
SABnzbd API client with improved error handling and type safety.
"""
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import PTN


class SABnzbdClient:
    """Client for interacting with SABnzbd API."""

    def __init__(self, url: str, api_key: str, enable_priority_logging: bool = False):
        """
        Initialize SABnzbd client.

        Args:
            url: SABnzbd base URL
            api_key: SABnzbd API key
            enable_priority_logging: Enable debug logging for priority parsing
        """
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.enable_priority_logging = enable_priority_logging

    async def _make_request(self, mode: str, extra_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to SABnzbd API.

        Args:
            mode: SABnzbd API mode
            extra_params: Additional parameters for the request

        Returns:
            JSON response from API

        Raises:
            Exception: If API request fails
        """
        params = {
            "apikey": self.api_key,
            "output": "json",
            "mode": mode
        }

        if extra_params:
            params.update(extra_params)

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"{self.url}/api", params=params) as response:
                if response.status != 200:
                    raise Exception(f"SABnzbd API error: {response.status}")
                return await response.json()

    async def get_queue(self) -> Dict[str, Any]:
        """Get the current download queue."""
        return await self._make_request("queue")

    async def get_history(self, limit: int = 100) -> Dict[str, Any]:
        """
        Get download history.

        Args:
            limit: Maximum number of history items to retrieve
        """
        return await self._make_request("history", {"limit": limit})

    async def set_priority(self, nzo_id: str, priority: int) -> Dict[str, Any]:
        """
        Set priority for a download.

        Args:
            nzo_id: SABnzbd download ID
            priority: Priority value (-1=Low, 0=Normal, 1=High, 2=Force)
        """
        return await self._make_request("queue", {
            "name": "priority",
            "value": nzo_id,
            "value2": priority
        })

    def _normalize_episode(self, episode: Any) -> Optional[int]:
        """
        Normalize episode field to int or None.

        This fixes the critical bug where PTN sometimes returns empty lists.

        Args:
            episode: Raw episode value from PTN (can be int, list, or None)

        Returns:
            int or None (NEVER a list)

        Examples:
            _normalize_episode(5) -> 5
            _normalize_episode([12, 13]) -> 12  (multi-episode, take first)
            _normalize_episode([]) -> None  (empty list)
            _normalize_episode(None) -> None
        """
        if episode is None:
            return None

        # CRITICAL FIX: Handle list types (including empty lists)
        if isinstance(episode, list):
            if len(episode) > 0:
                # Multi-episode file (e.g., S01E12E13) - take first episode
                return int(episode[0]) if isinstance(episode[0], (int, str)) else None
            else:
                # Empty list - convert to None
                return None

        # Single episode number
        try:
            return int(episode)
        except (ValueError, TypeError):
            return None

    def parse_queue_items(self, queue_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse queue data into standardized format.

        Args:
            queue_data: Raw queue data from SABnzbd API

        Returns:
            List of parsed download dictionaries
        """
        items = []

        if not queue_data or "queue" not in queue_data:
            return items

        queue = queue_data["queue"]
        slots = queue.get("slots", [])
        queue_paused = queue.get("paused", False)

        # Global speed for the entire queue
        global_speed_str = queue.get("speed", "0 KB/s")
        global_speed_mb = self._parse_speed_to_mb(global_speed_str)

        for position, slot in enumerate(slots, start=1):
            status = slot.get("status", "")

            # Determine item status
            if status in ["Paused"] or queue_paused:
                item_status = "paused"
            elif position == 1:
                # Position #1 is always the active download
                item_status = "downloading"
            else:
                # Everything else is queued
                item_status = "queued"

            # Use global speed only for actively downloading items
            percentage = float(slot.get("percentage", 0))
            if item_status == "downloading" and percentage > 0:
                item_speed = global_speed_mb
            else:
                item_speed = 0.0

            priority_value = slot.get("priority")

            # Debug logging
            if self.enable_priority_logging and position <= 3:
                print(f"[Priority Debug] Pos {position}: {repr(priority_value)} ({type(priority_value).__name__})")

            # Parse filename to extract season/episode
            filename = slot.get("filename", "")
            parsed = PTN.parse(filename)
            season = parsed.get("season")
            episode = parsed.get("episode")

            # CRITICAL FIX: Normalize episode to prevent list type errors
            episode = self._normalize_episode(episode)

            # Normalize season as well (just to be safe)
            if isinstance(season, list):
                season = season[0] if len(season) > 0 else None
            elif season is not None:
                try:
                    season = int(season)
                except (ValueError, TypeError):
                    season = None

            items.append({
                "id": slot.get("nzo_id"),
                "name": slot.get("filename"),
                "status": item_status,
                "detailed_status": status,
                "progress": float(slot.get("percentage", 0)),
                "size_total": float(slot.get("mb", 0)),
                "size_left": float(slot.get("mbleft", 0)),
                "time_left": slot.get("timeleft", "0:00:00"),
                "speed": item_speed,
                "category": slot.get("cat"),
                "priority": priority_value,
                "queue_position": position,
                "season": season,
                "episode": episode,
            })

        return items

    def _parse_speed_to_mb(self, speed_str: str) -> float:
        """
        Parse SABnzbd speed string to MB/s float.

        Examples:
            '12.3 MB/s' -> 12.3
            '500 KB/s' -> 0.5
            '1.2 GB/s' -> 1200.0
        """
        try:
            import re
            match = re.search(r'([\d.]+)\s*(KB/s|MB/s|GB/s|B/s|K|M|G)', speed_str, re.IGNORECASE)
            if not match:
                return 0.0

            value = float(match.group(1))
            unit = match.group(2).upper()

            if unit in ['KB/S', 'K']:
                return value / 1024
            elif unit in ['MB/S', 'M']:
                return value
            elif unit in ['GB/S', 'G']:
                return value * 1024
            elif unit == 'B/S':
                return value / (1024 * 1024)

            return 0.0
        except Exception:
            return 0.0

    def parse_history_items(self, history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse history data into standardized format.

        Args:
            history_data: Raw history data from SABnzbd API

        Returns:
            List of parsed download dictionaries
        """
        items = []

        if not history_data or "history" not in history_data:
            return items

        history = history_data["history"]
        slots = history.get("slots", [])

        for slot in slots:
            status_raw = slot.get("status", "")
            failed = slot.get("fail_message", "") != "" or status_raw == "Failed"

            item_status = "failed" if failed else "completed"

            # Parse completion time
            completed_at = None
            if slot.get("completed"):
                try:
                    completed_at = datetime.fromtimestamp(int(slot.get("completed")))
                except:
                    completed_at = None

            # Parse filename to extract season/episode
            filename = slot.get("name", "")
            parsed = PTN.parse(filename)
            season = parsed.get("season")
            episode = parsed.get("episode")

            # CRITICAL FIX: Normalize episode to prevent list type errors
            episode = self._normalize_episode(episode)

            # Normalize season
            if isinstance(season, list):
                season = season[0] if len(season) > 0 else None
            elif season is not None:
                try:
                    season = int(season)
                except (ValueError, TypeError):
                    season = None

            items.append({
                "id": slot.get("nzo_id"),
                "name": slot.get("name"),
                "status": item_status,
                "progress": 100.0 if not failed else 0.0,
                "size_total": float(slot.get("bytes", 0)) / (1024 * 1024),
                "category": slot.get("category"),
                "completed_at": completed_at,
                "failed": failed,
                "failure_reason": slot.get("fail_message"),
                "season": season,
                "episode": episode,
            })

        return items
