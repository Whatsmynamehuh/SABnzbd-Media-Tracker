import aiohttp
from typing import List, Dict, Any, Optional
import re
import PTN


class ArrClient:
    """Client for Radarr/Sonarr API."""

    def __init__(self, name: str, url: str, api_key: str, arr_type: str = "radarr", category: str = None):
        self.name = name
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.arr_type = arr_type  # "radarr" or "sonarr"
        self.category = category  # SABnzbd category this instance handles

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
        """Search for a movie/show by title using multi-stage matching."""
        # Parse release name using PTN to extract clean title
        parsed = PTN.parse(title)

        # Get parsed title and year
        parsed_title = parsed.get('title', title)
        download_year = parsed.get('year')

        print(f"[PTN Parse] Raw: '{title}' -> Title: '{parsed_title}', Year: {download_year}")

        # Clean the parsed title for better matching
        clean_title = self._clean_title(parsed_title)
        print(f"[Match Debug] Cleaned search title: '{clean_title}'")

        # Get all items from Radarr/Sonarr
        if self.arr_type == "radarr":
            items = await self._make_request("movie")
        else:
            items = await self._make_request("series")

        if not items:
            return None

        print(f"[Match Debug] Searching {len(items)} items in {self.name}")

        # Build list of candidates with match scores
        candidates = []
        all_titles_sample = []

        for item in items:
            item_title_raw = item.get("title", "")
            item_title = self._clean_title(item_title_raw)
            item_year = item.get("year")

            # Keep first 3 titles for debugging
            if len(all_titles_sample) < 3:
                all_titles_sample.append(item_title_raw)

            # Calculate match score
            score = self._calculate_match_score(clean_title, item_title, download_year, item_year)

            if score > 0:
                candidates.append({
                    "item": item,
                    "score": score,
                    "title": item_title_raw
                })

        # Show sample of library titles
        print(f"[Match Debug] Sample titles in library: {all_titles_sample}")

        # Show top 3 candidates if any
        if candidates:
            candidates.sort(key=lambda x: x["score"], reverse=True)
            for idx, c in enumerate(candidates[:3]):
                print(f"[Match Debug] Top candidate #{idx+1}: '{c['title']}' - Score: {c['score']}")

        # Sort by score (highest first) and return best match
        if candidates:
            candidates.sort(key=lambda x: x["score"], reverse=True)
            best_match = candidates[0]
            print(f"[Match Debug] Best match: '{best_match['title']}' with score {best_match['score']}")

            # Only return if score meets minimum threshold
            if best_match["score"] >= 60:  # Minimum 60% match
                return self._format_item(best_match["item"])
            else:
                print(f"[Match Debug] Best score {best_match['score']} is below threshold of 60")
        else:
            print(f"[Match Debug] No candidates with score > 0")

        return None

    def _calculate_match_score(self, download_title: str, item_title: str, download_year: Optional[int], item_year: Optional[int]) -> int:
        """
        Calculate match score between download title and media item.
        Returns score from 0-100, where 100 is perfect match.
        """
        if not download_title or not item_title:
            return 0

        score = 0

        # Stage 1: Exact match (100 points)
        if download_title == item_title:
            score = 100
        else:
            # Stage 2: Word-based matching
            download_words = set(download_title.split())
            item_words = set(item_title.split())

            # Remove very common words that don't help matching
            stop_words = {'the', 'a', 'an', 'of', 'and', 'or', 'in', 'to', 'for'}
            download_words = download_words - stop_words
            item_words = item_words - stop_words

            if not download_words or not item_words:
                return 0

            # Calculate word overlap percentage
            common_words = download_words & item_words
            word_overlap = len(common_words) / max(len(download_words), len(item_words))

            # Require significant word overlap
            if word_overlap < 0.5:  # At least 50% word overlap
                return 0

            # Base score on word overlap (0-70 points)
            score = int(word_overlap * 70)

            # Bonus: All item words present in download (important for short titles)
            if item_words.issubset(download_words):
                score += 20

        # Stage 3: Year matching bonus (up to +30 points or -50 penalty)
        if download_year and item_year:
            if download_year == item_year:
                score += 30  # Perfect year match
            elif abs(download_year - item_year) <= 1:
                score += 10  # Close year match (off by 1)
            else:
                score -= 50  # Wrong year is a strong negative signal

        return max(0, min(100, score))  # Clamp to 0-100

    def _clean_title(self, title: str) -> str:
        """Clean a title for comparison (PTN already removes most junk)."""
        # Remove ALL punctuation and special characters, keep only letters, numbers, spaces
        title = re.sub(r'[._-]', ' ', title)  # Replace separators with spaces
        title = re.sub(r'[^\w\s]', '', title)  # Remove all punctuation (!, :, etc)
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
            client = ArrClient(
                name=config["name"],
                url=config["url"],
                api_key=config["api_key"],
                arr_type="radarr",
                category=config.get("category")  # Optional category mapping
            )
            self.clients.append(client)
            print(f"[Category Config] Loaded {client.name} with category: {client.category}")

        # Initialize Sonarr clients
        for config in sonarr_configs:
            client = ArrClient(
                name=config["name"],
                url=config["url"],
                api_key=config["api_key"],
                arr_type="sonarr",
                category=config.get("category")  # Optional category mapping
            )
            self.clients.append(client)
            print(f"[Category Config] Loaded {client.name} with category: {client.category}")

    async def search_all(self, title: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Search specific Radarr/Sonarr instance based on category.
        NO FALLBACK - only searches the instance where category matches.
        """
        if not category:
            # No category = no search
            return None

        print(f"[Category Match] Looking for category '{category}' among {len(self.clients)} instances")

        # Find the client that handles this category
        for client in self.clients:
            print(f"[Category Match] Checking {client.name}: client.category='{client.category}' vs search='{category}' | Match: {client.category == category}")
            if client.category and client.category == category:
                print(f"[Poster Match] Searching '{client.name}' for '{title}' (category: {category})")
                result = await client.search_by_title(title)
                if result:
                    print(f"[Poster Match] ✓ Found in '{client.name}': {result.get('media_title')}")
                else:
                    print(f"[Poster Match] ✗ Not found in '{client.name}'")
                return result

        # No instance configured for this category
        print(f"[Poster Match] ⚠️  No instance configured for category '{category}'")
        return None
