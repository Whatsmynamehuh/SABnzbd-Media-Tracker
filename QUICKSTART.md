# Quick Start Guide

## First Time Setup

### 1. Configure Your Instances

```bash
cp config.example.yml config.yml
```

Edit `config.yml` and add your:
- SABnzbd URL and API key
- Radarr instance(s) URL and API key
- Sonarr instance(s) URL and API key

### 2. Run the Interactive Startup Script

**Linux/Mac:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

### 3. Choose Your Option

```
╔════════════════════════════════════════════════════════════╗
║        SABnzbd Media Tracker - Deployment Options         ║
╚════════════════════════════════════════════════════════════╝

Select deployment method:

  1) 🚀 Start in Development Mode (Accessible from network)
  2) 🐳 Deploy with Docker Compose
  3) ❌ Exit

Enter your choice [1-3]:
```

**For most users, choose Option 1** (Development Mode)

### 4. Access the App

The script will show you something like:

```
════════════════════════════════════════════════════════════
  ✅ SABnzbd Media Tracker is RUNNING!
════════════════════════════════════════════════════════════

  📱 Access from this server:
     http://localhost:3000

  🌐 Access from other devices on your network:
     http://192.168.1.100:3000

  💡 Tip: Bookmark this URL on your phone/tablet!

════════════════════════════════════════════════════════════
```

**Open your browser to the network URL** (e.g., `http://192.168.1.100:3000`)

## Accessing from Other Devices

### From Your Phone
1. Make sure your phone is on the **same WiFi network** as your server
2. Open your phone's browser
3. Go to the **network URL** shown by the script (e.g., `http://192.168.1.100:3000`)
4. Bookmark it for quick access!

### From Your Tablet/Laptop
Same steps as above - just use the network URL on any device on your home network.

## Features Overview

Once you're in, you'll see:

- **Stats Bar** - Real-time download counts and total speed
- **Navigation** - Switch between Downloading/Queued/Completed
- **Download Cards** - Each with:
  - Movie/TV show poster
  - Progress bar (orange for downloading)
  - Download speed and ETA
  - Size info
  - Priority controls (for queued items)

## Common Issues

### Can't access from other devices?
- Make sure both devices are on the **same network**
- Check your **firewall** isn't blocking ports 3000 and 3001
- Try the exact IP address shown by the script

### No posters showing?
- Verify your Radarr/Sonarr URLs are correct in `config.yml`
- Check API keys are valid
- Make sure the download name matches something in Radarr/Sonarr

### Backend won't start?
- Make sure `config.yml` exists and is properly formatted
- Check SABnzbd is running and accessible
- Verify Python 3.9+ is installed: `python3 --version`

## Stopping the App

**Development Mode:**
- Press `Ctrl+C` in the terminal

**Docker Mode:**
```bash
docker-compose down
```

## Need Help?

See the full [README.md](README.md) for detailed documentation.
