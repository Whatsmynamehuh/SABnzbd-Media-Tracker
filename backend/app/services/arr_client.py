"""
Radarr/Sonarr API client with improved error handling and retry logic.
"""
import aiohttp
from typing import List, Dict, Any, Optional
import re
import PTN
import asyncio


class ArrClient:
    """Client for Radarr/Sonarr API with retry logic."""

    def __init__(
        self,
        name: str,
        url: str,
        api_key: str,
        arr_type: str = "radarr",
        category: Optional[str] = None,
        enable_parsing_logging: bool = False,
        enable_match_logging: bool = False,
        enable_poster_logging: bool = False
    ):
        """
        Initialize Arr client.

        Args:
            name: Instance name
            url: Radarr/Sonarr URL
            api_key: API key
            arr_type: "radarr" or "sonarr"
            category: SABnzbd category this instance handles
            enable_parsing_logging: Enable parsing debug logs
            enable_match_logging: Enable match debug logs
            enable_poster_logging: Enable poster debug logs
        """
        self.name = name
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.arr_type = arr_type
        self.category = category
        self.enable_parsing_logging = enable_parsing_logging
        self.enable_match_logging = enable_match_logging
        self.enable_poster_logging = enable_poster_logging

    async def _make_request(
        self,
        endpoint: str,
        max_retries: int = 3,
        timeout: int = 10
    ) -> Optional[Any]:
        """
        Make a request to Radarr/Sonarr API with retry logic.

        Args:
            endpoint: API endpoint
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds

        Returns:
            JSON response or None if failed
        """
        headers = {"X-Api-Key": self.api_key}

        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{self.url}/api/v3/{endpoint}",
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    print(f"Error connecting to {self.name} after {max_retries} attempts: {e}")
                    return None

        return None

    async def search_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """
        Search for a movie/show by title using multi-stage matching.

        Args:
            title: Release name or title to search for

        Returns:
            Media info dict or None if not found
        """
        # Parse release name using PTN
        parsed = PTN.parse(title)
        parsed_title = parsed.get('title', title)
        download_year = parsed.get('year')

        if self.enable_parsing_logging:
            print(f"[PTN Parse] '{title}' -> Title: '{parsed_title}', Year: {download_year}")

        clean_title = self._clean_title(parsed_title)

        if self.enable_match_logging:
            print(f"[Match Debug] Cleaned: '{clean_title}'")

        # Get all items from Radarr/Sonarr
        endpoint = "movie" if self.arr_type == "radarr" else "series"
        items = await self._make_request(endpoint)

        if not items:
            return None

        # Find best match
        candidates = []
        for item in items:
            item_title_raw = item.get("title", "")
            item_title = self._clean_title(item_title_raw)
            item_year = item.get("year")

            score = self._calculate_match_score(clean_title, item_title, download_year, item_year)

            if score > 0:
                candidates.append({
                    "item": item,
                    "score": score,
                    "title": item_title_raw
                })

        if candidates:
            candidates.sort(key=lambda x: x["score"], reverse=True)
            best_match = candidates[0]

            if self.enable_match_logging:
                print(f"[Match Debug] Best: '{best_match['title']}' (score: {best_match['score']})")

            # Return if score meets threshold
            if best_match["score"] >= 60:
                return self._format_item(best_match["item"])

        return None

    def _calculate_match_score(
        self,
        download_title: str,
        item_title: str,
        download_year: Optional[int],
        item_year: Optional[int]
    ) -> int:
        """
        Calculate match score between download title and media item.

        Args:
            download_title: Cleaned download title
            item_title: Cleaned library title
            download_year: Year from download
            item_year: Year from library

        Returns:
            Score from 0-100 (100 = perfect match)
        """
        if not download_title or not item_title:
            return 0

        # Exact match
        if download_title == item_title:
            score = 100
        else:
            # Word-based matching
            download_words = set(download_title.split())
            item_words = set(item_title.split())

            # Remove stop words
            stop_words = {'the', 'a', 'an', 'of', 'and', 'or', 'in', 'to', 'for'}
            download_words = download_words - stop_words
            item_words = item_words - stop_words

            if not download_words or not item_words:
                return 0

            # Word overlap
            common_words = download_words & item_words
            word_overlap = len(common_words) / max(len(download_words), len(item_words))

            if word_overlap < 0.5:
                return 0

            score = int(word_overlap * 70)

            # Bonus if all item words present
            if item_words.issubset(download_words):
                score += 20

        # Year matching
        if download_year and item_year:
            if download_year == item_year:
                score += 30
            elif abs(download_year - item_year) <= 1:
                score += 10
            else:
                score -= 50

        return max(0, min(100, score))

    def _clean_title(self, title: str) -> str:
        """Clean title for comparison."""
        title = re.sub(r'[._-]', ' ', title)
        title = re.sub(r'[^\w\s]', '', title)
        title = re.sub(r'\s+', ' ', title).strip().lower()

        # Normalize abbreviations
        abbreviations = {
            r'\bdr\b': 'doctor',
            r'\bmr\b': 'mister',
            r'\bmrs\b': 'missus',
            r'\bst\b': 'saint',
        }
        for abbr, full in abbreviations.items():
            title = re.sub(abbr, full, title)

        # Roman numerals to numbers
        roman_map = [
            (r'\bviii\b', '8'), (r'\bvii\b', '7'), (r'\bvi\b', '6'),
            (r'\bix\b', '9'), (r'\biv\b', '4'), (r'\bv\b', '5'),
            (r'\biii\b', '3'), (r'\bii\b', '2'), (r'\bx\b', '10'), (r'\bi\b', '1'),
        ]
        for roman, arabic in roman_map:
            title = re.sub(roman, arabic, title)

        return title

    def _format_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Format item into standardized response."""
        return {
            "media_type": "movie" if self.arr_type == "radarr" else "tv",
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
                remote_url = image.get("remoteUrl")
                if remote_url:
                    return remote_url

                url = image.get("url")
                if url:
                    if url.startswith("/"):
                        return f"{self.url}{url}"
                    return url

        return None


class ArrManager:
    """Manages multiple Radarr/Sonarr instances."""

    def __init__(
        self,
        radarr_configs: List[Dict],
        sonarr_configs: List[Dict],
        enable_category_logging: bool = False,
        enable_parsing_logging: bool = False,
        enable_match_logging: bool = False,
        enable_poster_logging: bool = False
    ):
        """
        Initialize Arr manager with multiple instances.

        Args:
            radarr_configs: List of Radarr configuration dicts
            sonarr_configs: List of Sonarr configuration dicts
            enable_category_logging: Enable category debug logs
            enable_parsing_logging: Enable parsing debug logs
            enable_match_logging: Enable match debug logs
            enable_poster_logging: Enable poster debug logs
        """
        self.clients: List[ArrClient] = []
        self.enable_category_logging = enable_category_logging
        self.enable_poster_logging = enable_poster_logging

        # Initialize Radarr clients
        for config in radarr_configs:
            client = ArrClient(
                name=config["name"],
                url=config["url"],
                api_key=config["api_key"],
                arr_type="radarr",
                category=config.get("category"),
                enable_parsing_logging=enable_parsing_logging,
                enable_match_logging=enable_match_logging,
                enable_poster_logging=enable_poster_logging
            )
            self.clients.append(client)

            if enable_category_logging:
                print(f"[Category Config] Loaded {client.name} -> category: {client.category}")

        # Initialize Sonarr clients
        for config in sonarr_configs:
            client = ArrClient(
                name=config["name"],
                url=config["url"],
                api_key=config["api_key"],
                arr_type="sonarr",
                category=config.get("category"),
                enable_parsing_logging=enable_parsing_logging,
                enable_match_logging=enable_match_logging,
                enable_poster_logging=enable_poster_logging
            )
            self.clients.append(client)

            if enable_category_logging:
                print(f"[Category Config] Loaded {client.name} -> category: {client.category}")

    async def search_all(self, title: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Search for media in the appropriate Arr instance based on category.

        Args:
            title: Release name or title
            category: SABnzbd category

        Returns:
            Media info dict or None
        """
        if not category:
            return None

        if self.enable_category_logging:
            print(f"[Category Match] Looking for category '{category}'")

        # Find matching client
        for client in self.clients:
            if client.category and client.category == category:
                if self.enable_poster_logging:
                    print(f"[Poster Match] Searching '{client.name}' for '{title}'")

                result = await client.search_by_title(title)

                if self.enable_poster_logging:
                    if result:
                        print(f"[Poster Match] ✓ Found in '{client.name}': {result.get('media_title')}")
                    else:
                        print(f"[Poster Match] ✗ Not found in '{client.name}'")

                return result

        if self.enable_poster_logging:
            print(f"[Poster Match] ⚠️ No instance for category '{category}'")

        return None
