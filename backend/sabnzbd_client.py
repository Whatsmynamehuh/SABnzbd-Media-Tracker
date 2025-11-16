import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime


class SABnzbdClient:
    def __init__(self, url: str, api_key: str):
        self.url = url.rstrip('/')
        self.api_key = api_key

    async def _make_request(self, mode: str, extra_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a request to SABnzbd API."""
        params = {
            "apikey": self.api_key,
            "output": "json",
            "mode": mode
        }

        if extra_params:
            params.update(extra_params)

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.url}/api", params=params) as response:
                if response.status != 200:
                    raise Exception(f"SABnzbd API error: {response.status}")
                return await response.json()

    async def get_queue(self) -> Dict[str, Any]:
        """Get the current queue with all downloads."""
        return await self._make_request("queue")

    async def get_history(self, limit: int = 100) -> Dict[str, Any]:
        """Get download history."""
        return await self._make_request("history", {"limit": limit})

    async def set_priority(self, nzo_id: str, priority: int) -> Dict[str, Any]:
        """
        Set priority for a download.
        Priority: -100 (Default), -1 (Paused), 0 (Low), 1 (Normal), 2 (High), 3 (Force)
        """
        return await self._make_request("queue", {
            "name": "priority",
            "value": nzo_id,
            "value2": priority
        })

    async def pause_download(self, nzo_id: str) -> Dict[str, Any]:
        """Pause a download."""
        return await self._make_request("queue", {
            "name": "pause",
            "value": nzo_id
        })

    async def resume_download(self, nzo_id: str) -> Dict[str, Any]:
        """Resume a download."""
        return await self._make_request("queue", {
            "name": "resume",
            "value": nzo_id
        })

    async def delete_from_queue(self, nzo_id: str) -> Dict[str, Any]:
        """Delete a download from queue."""
        return await self._make_request("queue", {
            "name": "delete",
            "value": nzo_id
        })

    async def delete_from_history(self, nzo_id: str) -> Dict[str, Any]:
        """Delete a download from history."""
        return await self._make_request("history", {
            "name": "delete",
            "value": nzo_id
        })

    def parse_queue_items(self, queue_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse queue data into standardized format."""
        items = []

        if not queue_data or "queue" not in queue_data:
            return items

        queue = queue_data["queue"]
        slots = queue.get("slots", [])
        queue_paused = queue.get("paused", False)

        # CRITICAL: Use GLOBAL queue speed, not per-item mbpersec!
        # SABnzbd provides a global speed field that's always accurate
        global_speed_str = queue.get("speed", "0 KB/s")
        # Parse speed string like "12.3 MB/s" or "500 KB/s" to MB/s
        global_speed_mb = self._parse_speed_to_mb(global_speed_str)

        for position, slot in enumerate(slots, start=1):
            # Determine status
            status = slot.get("status", "")

            # CRITICAL: SABnzbd can only download ONE item at a time
            # Position #1 is the active download, everything else is queued
            if status in ["Paused"] or queue_paused:
                item_status = "paused"
            elif position == 1:
                # Position #1 is ALWAYS the active item (downloading, extracting, verifying, etc.)
                # Include all post-processing statuses: Extracting, Verifying, Repairing, Moving, QuickCheck
                item_status = "downloading"
            else:
                # Everything else is queued (positions 2, 3, 4...)
                item_status = "queued"

            # Use global speed for actively downloading items only
            percentage = float(slot.get("percentage", 0))
            if item_status == "downloading" and percentage > 0:
                item_speed = global_speed_mb
            else:
                item_speed = 0.0

            priority_value = slot.get("priority")

            # Debug: Log RAW priority value and entire slot for top 3 items
            if position <= 3:
                print(f"[RAW Priority Debug] Pos {position}: RAW value = {repr(priority_value)} (type: {type(priority_value).__name__})")
                print(f"[RAW Priority Debug] Pos {position}: Full slot data = {slot}")

            items.append({
                "id": slot.get("nzo_id"),
                "name": slot.get("filename"),
                "status": item_status,
                "detailed_status": status,  # Actual SABnzbd status (Downloading, Extracting, etc.)
                "progress": float(slot.get("percentage", 0)),
                "size_total": float(slot.get("mb", 0)),
                "size_left": float(slot.get("mbleft", 0)),
                "time_left": slot.get("timeleft", "0:00:00"),
                "speed": item_speed,
                "category": slot.get("cat"),
                "priority": priority_value,
                "queue_position": position,  # Track position in queue
            })

        return items

    def _parse_speed_to_mb(self, speed_str: str) -> float:
        """Parse SABnzbd speed string to MB/s float.
        Examples: '12.3 MB/s' -> 12.3, '500 KB/s' -> 0.5, '1.2 GB/s' -> 1200.0
        """
        try:
            import re
            match = re.search(r'([\d.]+)\s*(KB/s|MB/s|GB/s|B/s|K|M|G)', speed_str, re.IGNORECASE)
            if not match:
                return 0.0

            value = float(match.group(1))
            unit = match.group(2).upper()

            # Handle different unit formats
            if unit in ['KB/S', 'K']:
                return value / 1024  # Convert KB/s to MB/s
            elif unit in ['MB/S', 'M']:
                return value
            elif unit in ['GB/S', 'G']:
                return value * 1024  # Convert GB/s to MB/s
            elif unit == 'B/S':
                return value / (1024 * 1024)  # Convert B/s to MB/s

            return 0.0
        except Exception:
            return 0.0

    def parse_history_items(self, history_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse history data into standardized format."""
        items = []

        if not history_data or "history" not in history_data:
            return items

        history = history_data["history"]
        slots = history.get("slots", [])

        for slot in slots:
            # Determine status
            status_raw = slot.get("status", "")
            failed = slot.get("fail_message", "") != "" or status_raw == "Failed"

            if failed:
                item_status = "failed"
            else:
                item_status = "completed"

            # Parse completion time
            completed_at = None
            if slot.get("completed"):
                try:
                    completed_at = datetime.fromtimestamp(int(slot.get("completed")))
                except:
                    completed_at = None

            items.append({
                "id": slot.get("nzo_id"),
                "name": slot.get("name"),
                "status": item_status,
                "progress": 100.0 if not failed else 0.0,
                "size_total": float(slot.get("bytes", 0)) / (1024 * 1024),  # Convert to MB
                "category": slot.get("category"),
                "completed_at": completed_at,
                "failed": failed,
                "failure_reason": slot.get("fail_message"),
            })

        return items
