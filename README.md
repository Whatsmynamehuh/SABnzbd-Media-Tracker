# SABnzbd Media Progress Tracker

A beautiful, real-time web interface for monitoring your SABnzbd downloads with automatic poster fetching from Radarr and Sonarr instances.

![SABnzbd Media Tracker](https://img.shields.io/badge/Status-Production%20Ready-green)

<img width="1637" height="908" alt="image" src="https://github.com/user-attachments/assets/a572ffed-3e2e-4451-8183-f64fe3e5c5ee" />


## Features

- **Real-time Progress Tracking**: Auto-refreshing every 2 seconds to show live download progress
- **Media Posters**: Automatically fetches movie/TV show posters from your Radarr and Sonarr instances
- **Smart Search**: Quickly find downloads by title, filename, season/episode (S01E02), or category with real-time filtering
- **Season/Episode Display**: TV shows automatically show season and episode numbers (e.g., S06E18) parsed from filenames
- **Organized Sections**:
  - 🔥 **Downloading**: Active downloads with detailed status (Downloading, Extracting, Verifying, etc.)
  - 📋 **Queued**: Waiting downloads with visual priority indicators and position numbers
  - ✅ **Completed**: Finished downloads (auto-cleaned after 48 hours)
  - ⚠️ **Failed**: Failed downloads with detailed error messages
- **Priority Management**: Change download priorities directly from the interface with correct SABnzbd values (Force, High, Normal, Low)
- **Category-based Matching**: Intelligent routing to correct Radarr/Sonarr instance based on SABnzbd categories
- **Advanced Title Matching**: Uses Parse Torrent Name (PTN) for accurate media detection and metadata extraction
- **Horizontal Scroll Navigation**: Smooth card-based layout with touch support for mobile browsing
- **Responsive Design**: Full mobile support with touch-optimized controls and adaptive layouts
- **Multiple Instances**: Support for unlimited Radarr/Sonarr instances with per-category routing
- **Auto Cleanup**: Completed downloads automatically removed after 48 hours (configurable)

## Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: Database ORM with async support
- **SQLite**: Lightweight database
- **aiohttp**: Async HTTP client for API calls
- **APScheduler**: Background task scheduling
- **PTN (Parse Torrent Name)**: Intelligent media name parsing

### Frontend
- **React 18**: Modern UI library
- **Vite**: Lightning-fast build tool
- **Tailwind CSS**: Utility-first CSS framework
- **SWR**: Data fetching and caching
- **Axios**: HTTP client

## Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- SABnzbd instance with API access
- (Optional) Radarr and/or Sonarr instances for poster support

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/SABnzbd-Media-Tracker.git
cd SABnzbd-Media-Tracker
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy and configure the config file
cp config.example.yml config.yml
# Edit config.yml with your settings
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

## Configuration

Edit `config.yml` with your settings:

```yaml
sabnzbd:
  url: "http://localhost:8080"
  api_key: "your_sabnzbd_api_key"

radarr:
  - name: "Radarr-Movies"
    url: "http://localhost:7878"
    api_key: "your_radarr_api_key"
    category: "radarr-movies"  # Match SABnzbd category

  - name: "Radarr-Movies-Animation"
    url: "http://localhost:7879"
    api_key: "your_radarr_api_key"
    category: "radarr-movies-animation"

  - name: "Radarr-Movies-Anime"
    url: "http://localhost:7880"
    api_key: "your_radarr_api_key"
    category: "radarr-movies-anime"

sonarr:
  - name: "Sonarr"
    url: "http://localhost:8989"
    api_key: "your_sonarr_api_key"
    category: "sonarr-tvshows"

  - name: "Sonarr-TvShows-Animation"
    url: "http://localhost:8990"
    api_key: "your_sonarr_api_key"
    category: "sonarr-tvshows-animation"

  - name: "Sonarr-TvShows-Anime"
    url: "http://localhost:8991"
    api_key: "your_sonarr_api_key"
    category: "sonarr-tvshows-anime"

server:
  host: "0.0.0.0"
  port: 3001

cleanup:
  completed_after_hours: 48
  check_interval_minutes: 60
```

**Category-based Matching:**
The `category` field links each Radarr/Sonarr instance to specific SABnzbd categories. This ensures:
- Downloads are matched to the correct library
- Posters are fetched from the right instance
- Supports multiple instances for different media types (4K, 1080p, anime, animation, etc.)

### Finding Your API Keys

**SABnzbd:**
- Go to SABnzbd Web UI → Config → General
- Copy the API Key

**Radarr/Sonarr:**
- Go to Settings → General → Security
- Copy the API Key

## Usage

### Quick Start with Interactive Scripts (Recommended)

We provide interactive startup scripts that give you deployment options:

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

**You'll see a menu with options:**
1. **🚀 Start in Development Mode** - Run directly (accessible from network)
2. **🐳 Deploy with Docker Compose** - Run in containers
3. **❌ Exit**

The scripts will:
- ✅ Check all dependencies
- ✅ Install missing packages
- ✅ Auto-detect your server's IP address
- ✅ Show you the exact URL to access from other devices

### Network Access

When you start the app, the script will show you:

```
✅ SABnzbd Media Tracker is RUNNING!

📱 Access from this server:
   http://localhost:3000

🌐 Access from other devices on your network:
   http://192.168.1.100:3000  ← Use this on your phone/tablet!
```

**Perfect for:**
- 📱 Accessing from your phone while on the couch
- 💻 Monitoring from your laptop anywhere in the house
- 📺 Displaying on a tablet mounted on the wall

### Manual Development Mode

If you prefer to run manually:

```bash
# Terminal 1 - Backend
python -m backend.main

# Terminal 2 - Frontend
cd frontend
npm run dev
```

The application will be available at:
- **Frontend**: http://localhost:3000 or http://YOUR_SERVER_IP:3000
- **Backend API**: http://localhost:3001

### Docker Compose Deployment

For production use with automatic restarts:

```bash
docker-compose up -d --build
```

View logs: `docker-compose logs -f`
Stop: `docker-compose down`

## Features in Detail

### Real-time Monitoring

The interface automatically refreshes every 2 seconds to show:
- Current download progress with detailed status (Downloading, Extracting, Verifying, etc.)
- Download speeds in real-time
- Time remaining estimates
- Queue status and positions

### Smart Search

The built-in search feature allows you to quickly find downloads by:
- **Media Title**: Search by movie or TV show name
- **Filename**: Search the original download filename
- **Season/Episode**: Search by episode identifier (e.g., "s01e02", "S06E18")
- **Category**: Filter by SABnzbd category

Search is real-time and works across all sections (Downloading, Queued, Completed, Failed).

### Season/Episode Display

For TV shows, the tracker automatically:
- Parses filenames using PTN (Parse Torrent Name) library
- Extracts season and episode numbers
- Displays them in a prominent badge format (e.g., "S06E18")
- Shows episode info across all views (Hero, Queue, Cards)

This makes it easy to identify which episode is downloading without reading the full filename.

### Priority Management

For queued downloads, you can click to change priority levels:
- **Force** (Value: 2): Download immediately, bypassing the queue
- **High** (Value: 1): High priority in queue
- **Normal** (Value: 0): Default priority
- **Low** (Value: -1): Low priority in queue

Priority changes are reflected instantly in SABnzbd and the interface updates automatically.

### Auto Cleanup

Completed downloads are automatically removed from the database after 48 hours (configurable in `config.yml`).

### Failed Downloads

View and filter failed downloads with detailed error messages to help troubleshoot issues.

### Media Information

The tracker automatically matches downloads with your Radarr/Sonarr library to display:
- Movie/TV show posters
- Release year
- Media type (Movie or TV Show)
- Source instance

## API Endpoints

The backend provides a RESTful API:

- `GET /api/downloads` - Get all downloads
- `GET /api/downloads/downloading` - Get active downloads
- `GET /api/downloads/queued` - Get queued downloads
- `GET /api/downloads/completed` - Get completed downloads
- `GET /api/downloads/failed` - Get failed downloads
- `GET /api/stats` - Get download statistics
- `POST /api/downloads/{id}/priority` - Update download priority

## Troubleshooting

### Backend won't start

1. Check that `config.yml` exists and is properly formatted
2. Verify SABnzbd is running and accessible
3. Check Python version: `python --version` (requires 3.9+)
4. Ensure all Python dependencies are installed: `pip install -r requirements.txt`

### No posters showing

1. Verify Radarr/Sonarr URLs are correct and accessible
2. Check API keys are correct
3. Ensure the download name matches the media title in Radarr/Sonarr
4. Verify the `category` field in config.yml matches your SABnzbd categories exactly
5. Check backend logs for category matching errors

### Priority changes not working

1. Ensure you're using the correct SABnzbd priority values (Force=2, High=1, Normal=0, Low=-1)
2. Check that SABnzbd API is accessible and responding
3. Verify the download is in "queued" status (not currently downloading)
4. Check browser console for API errors

### Season/Episode not showing

1. Ensure the filename follows standard naming conventions (e.g., "Show.Name.S01E02....")
2. PTN library parses the filename - if the format is non-standard, it may not detect episodes
3. Check that the download is classified as `media_type: tv` in the database

### Search not finding downloads

1. Search is case-insensitive and searches across: title, filename, season/episode, and category
2. Try searching for partial matches (e.g., "s01" instead of "s01e02")
3. Clear the search and verify downloads appear without filtering
4. Check browser console for JavaScript errors

### Frontend can't connect to backend

1. Ensure backend is running on port 3001
2. Check browser console for CORS errors
3. Verify firewall settings allow connections on ports 3000 and 3001
4. If using Docker, ensure container networking is configured correctly

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Enjoy your automated media tracking!** 🎬📺
