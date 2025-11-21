# Migration Guide - v1.x to v2.0

## What's New in v2.0?

### 🐛 Critical Bug Fixes
1. **Episode List Bug** - Fixed SQLite error: `type 'list' is not supported`
   - PTN sometimes returns empty lists `[]` for episode fields
   - Now properly converts to `None` or extracts first episode number

2. **Failed Downloads Cleanup** - Failed downloads now get cleaned up after 48 hours
   - Previously only completed downloads were cleaned up
   - Failed downloads would accumulate forever

### ✨ Improvements
- Better project structure (organized into models, schemas, services, api)
- Pydantic v2 syntax (no more deprecated warnings)
- Multi-stage Docker builds (smaller images)
- Non-root Docker user (better security)
- Health checks in Docker Compose
- Relative paths in docker-compose.yml (portable)
- Environment variable support for sensitive data
- Better error handling and retry logic
- Type hints throughout the codebase

## Migration Steps

### Option 1: In-Place Upgrade (Recommended)

1. **Backup Your Data**
   ```bash
   # Backup your database
   cp media_tracker.db media_tracker.db.backup

   # Backup your config
   cp config.yml config.yml.backup
   ```

2. **Pull the Latest Code**
   ```bash
   git pull origin main
   ```

3. **Update Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Update Docker Compose Paths**

   Your `docker-compose.yml` now uses relative paths. If you have a custom docker-compose.yml:

   **Old:**
   ```yaml
   volumes:
     - /mnt/user/1. Appdata/Scripts/SABnzbd-Media-Tracker/config.yml:/app/config.yml:ro
     - /mnt/user/1. Appdata/Scripts/SABnzbd-Media-Tracker/data:/app/data
   ```

   **New:**
   ```yaml
   volumes:
     - ./config.yml:/app/config.yml:ro
     - ./data:/app/data
   ```

5. **Move Database to Data Directory (Optional but Recommended)**
   ```bash
   mkdir -p data
   mv media_tracker.db data/
   ```

6. **Restart the Application**
   ```bash
   # If using Docker:
   docker-compose down
   docker-compose up --build -d

   # If running manually:
   python -m backend.app.main
   ```

### Option 2: Fresh Install

1. **Backup Your Config**
   ```bash
   cp config.yml config.yml.backup
   ```

2. **Remove Old Installation**
   ```bash
   docker-compose down
   rm -rf backend/__pycache__
   ```

3. **Pull Latest Code**
   ```bash
   git pull origin main
   ```

4. **Rebuild and Start**
   ```bash
   docker-compose up --build -d
   ```

## Verifying the Migration

### 1. Check Backend Health
```bash
curl http://localhost:3001/
# Should return: {"status":"ok","message":"SABnzbd Media Tracker API","version":"2.0.0"}
```

### 2. Check Logs for Episode Errors
```bash
docker-compose logs -f backend | grep "Error binding parameter"
```
If you see NO errors, the episode bug is fixed! ✅

### 3. Check Failed Downloads Cleanup
After 48 hours, check that failed downloads are being removed:
```bash
docker-compose logs -f backend | grep "Cleanup"
```
You should see messages like:
```
[12:00:00] 🧹 Cleanup: 5 removed, 10 kept
[12:00:00]   ✅ Movie Name (completed 50h ago)
[12:00:00]   ❌ Failed Download (completed 49h ago)
```

## Troubleshooting

### Database Errors After Migration

If you see errors like "no such column", your database schema might be out of sync:

```bash
# Backup and recreate database
mv data/media_tracker.db data/media_tracker.db.old
# Restart the app - it will create a new database
docker-compose restart backend
```

### Import Errors

If you see import errors like `ModuleNotFoundError: No module named 'backend.app'`:

```bash
# Make sure you're running from the project root
cd /path/to/SABnzbd-Media-Tracker
python -m backend.app.main
```

### Docker Path Issues

If Docker can't find `config.yml`:

```bash
# Make sure config.yml is in the project root
ls -la config.yml

# Make sure you're running docker-compose from the project root
pwd  # Should be /path/to/SABnzbd-Media-Tracker
docker-compose up -d
```

## Rollback Plan

If something goes wrong:

1. **Stop the new version**
   ```bash
   docker-compose down
   ```

2. **Restore your backup**
   ```bash
   cp media_tracker.db.backup media_tracker.db
   cp config.yml.backup config.yml
   ```

3. **Checkout the old version**
   ```bash
   git checkout <previous-commit-hash>
   ```

4. **Restart**
   ```bash
   docker-compose up -d
   ```

## Getting Help

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Open an issue on GitHub with:
   - Error messages
   - Your config.yml (redact API keys!)
   - Docker logs

## What Changed Under the Hood

### File Structure
```
Old:                          New:
backend/                      backend/
├── main.py                   ├── app/
├── database.py               │   ├── main.py
├── config.py                 │   ├── database.py
├── sync_service.py           │   ├── config.py
├── sabnzbd_client.py         │   ├── models/
├── arr_client.py             │   │   └── download.py
└── logger.py                 │   ├── schemas/
                              │   │   └── download.py
                              │   ├── services/
                              │   │   ├── sabnzbd_client.py
                              │   │   ├── arr_client.py
                              │   │   └── sync_service.py
                              │   ├── api/
                              │   │   ├── downloads.py
                              │   │   └── stats.py
                              │   └── utils/
                              │       └── logger.py
                              └── requirements.txt
```

### Key Code Changes

1. **Episode Normalization** (`backend/app/services/sabnzbd_client.py`)
   ```python
   def _normalize_episode(self, episode: Any) -> Optional[int]:
       if isinstance(episode, list):
           return episode[0] if len(episode) > 0 else None
       return int(episode) if episode else None
   ```

2. **Cleanup Both Statuses** (`backend/app/services/sync_service.py`)
   ```python
   # Old:
   Download.status == "completed"

   # New:
   Download.status.in_(["completed", "failed"])
   ```

3. **Pydantic v2** (all schemas)
   ```python
   # Old:
   DownloadResponse.from_orm(d)

   # New:
   DownloadResponse.model_validate(d)
   ```
