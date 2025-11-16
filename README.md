# SABnzbd Media Progress Tracker

A beautiful, real-time web interface for monitoring your SABnzbd downloads with automatic poster fetching from Radarr and Sonarr instances.

![SABnzbd Media Tracker](https://img.shields.io/badge/Status-Production%20Ready-green)

## Features

- **Real-time Progress Tracking**: Auto-refreshing every 5 seconds to show live download progress
- **Media Posters**: Automatically fetches movie/TV show posters from your Radarr and Sonarr instances
- **Organized Sections**:
  - 🔥 **Downloading**: Active downloads with orange progress bars
  - ⏸️ **Queued**: Waiting downloads with priority management
  - ✅ **Completed**: Finished downloads (auto-cleaned after 48 hours)
  - ⚠️ **Failed**: Failed downloads with error messages
- **Priority Management**: Change download priorities directly from the interface
- **Horizontal Scroll Navigation**: Smooth card-based layout for easy browsing
- **Responsive Design**: Works on desktop and mobile devices
- **Multiple Instances**: Support for up to 6 Radarr/Sonarr instances
- **Auto Cleanup**: Completed downloads automatically removed after 48 hours

## Tech Stack

### Backend
- **FastAPI**: Modern, fast Python web framework
- **SQLAlchemy**: Database ORM with async support
- **SQLite**: Lightweight database
- **aiohttp**: Async HTTP client for API calls
- **APScheduler**: Background task scheduling

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
  - name: "Radarr 4K"
    url: "http://localhost:7878"
    api_key: "your_radarr_api_key"
  - name: "Radarr 1080p"
    url: "http://localhost:7879"
    api_key: "your_radarr_api_key"

sonarr:
  - name: "Sonarr 4K"
    url: "http://localhost:8989"
    api_key: "your_sonarr_api_key"
  - name: "Sonarr 1080p"
    url: "http://localhost:8990"
    api_key: "your_sonarr_api_key"

server:
  host: "0.0.0.0"
  port: 3001

cleanup:
  completed_after_hours: 48
  check_interval_minutes: 60
```

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

The interface automatically refreshes every 5 seconds to show:
- Current download progress
- Download speeds
- Time remaining
- Queue status

### Priority Management

For queued downloads, you can set priority levels:
- **Force**: Download immediately
- **High**: High priority
- **Normal**: Default priority
- **Low**: Low priority
- **Paused**: Pause the download

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

### No posters showing

1. Verify Radarr/Sonarr URLs are correct and accessible
2. Check API keys are correct
3. Ensure the download name matches the media title in Radarr/Sonarr

### Frontend can't connect to backend

1. Ensure backend is running on port 3001
2. Check browser console for CORS errors
3. Verify firewall settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Enjoy your automated media tracking!** 🎬📺
