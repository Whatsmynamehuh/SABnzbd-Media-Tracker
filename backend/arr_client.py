import aiohttp
from typing import List, Dict, Any, Optional
import re


class ArrClient:
    """Client for Radarr/Sonarr API."""

    def __init__(self, name: str, url: str, api_key: str, arr_type: str = "radarr"):
        self.name = name
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.arr_type = arr_type  # "radarr" or "sonarr"

    async def _make_request(self, endpoint: str) -> Any:
        """Make a request to Radarr/Sonarr API."""
        headers = {
            "X-Api-Key": self.api_key
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.url}/api/v3/{endpoint}", headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return None
                    return await response.json()
            except Exception as e:
                print(f"Error connecting to {self.name}: {e}")
                return None

    async def search_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search for a movie/show by title."""
        # Clean the title for better matching
        clean_title = self._clean_title(title)

        # Get all items from Radarr/Sonarr
        if self.arr_type == "radarr":
            items = await self._make_request("movie")
        else:
            items = await self._make_request("series")

        if not items:
            return None

        # Try to find a match
        for item in items:
            item_title = self._clean_title(item.get("title", ""))

            # Check if the cleaned download title contains the movie/show title
            if item_title in clean_title or clean_title in item_title:
                return self._format_item(item)

        return None

    def _clean_title(self, title: str) -> str:
        """Clean a title for comparison."""
        # Remove common patterns
        title = re.sub(r'\[.*?\]', '', title)  # Remove brackets
        title = re.sub(r'\(.*?\)', '', title)  # Remove parentheses
        title = re.sub(r'\d{3,4}p', '', title)  # Remove quality
        title = re.sub(r'(REPACK|PROPER|REAL|RETAIL)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'(BluRay|WEB-DL|WEBRip|HDTV|x264|x265|HEVC)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'[._-]', ' ', title)  # Replace separators with spaces
        title = re.sub(r'\s+', ' ', title).strip().lower()  # Normalize spaces
        return title

    def _format_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format item data into standardized format."""
        if self.arr_type == "radarr":
            return {
                "media_type": "movie",
                "media_title": item.get("title"),
                "year": item.get("year"),
                "poster_url": self._get_poster_url(item),
                "arr_instance": self.name
            }
        else:  # sonarr
            return {
                "media_type": "tv",
                "media_title": item.get("title"),
                "year": item.get("year"),
                "poster_url": self._get_poster_url(item),
                "arr_instance": self.name
            }

    def _get_poster_url(self, item: Dict[str, Any]) -> Optional[str]:
        """Extract poster URL from item."""
        images = item.get("images", [])

        for image in images:
            if image.get("coverType") == "poster":
                # Use remote URL if available, otherwise construct local URL
                remote_url = image.get("remoteUrl")
                if remote_url:
                    return remote_url

                url = image.get("url")
                if url:
                    # If it's a relative URL, make it absolute
                    if url.startswith("/"):
                        return f"{self.url}{url}"
                    return url

        return None


class ArrManager:
    """Manages multiple Radarr/Sonarr instances."""

    def __init__(self, radarr_configs: List[Dict], sonarr_configs: List[Dict]):
        self.clients = []

        # Initialize Radarr clients
        for config in radarr_configs:
            self.clients.append(ArrClient(
                name=config["name"],
                url=config["url"],
                api_key=config["api_key"],
                arr_type="radarr"
            ))

        # Initialize Sonarr clients
        for config in sonarr_configs:
            self.clients.append(ArrClient(
                name=config["name"],
                url=config["url"],
                api_key=config["api_key"],
                arr_type="sonarr"
            ))

    async def search_all(self, title: str) -> Optional[Dict[str, Any]]:
        """Search all Radarr/Sonarr instances for a title."""
        for client in self.clients:
            result = await client.search_by_title(title)
            if result:
                return result

        return None
