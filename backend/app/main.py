"""
SABnzbd Media Tracker - Main FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn

from backend.app.database import db
from backend.app.config import get_config
from backend.app.services import SyncService
from backend.app.utils import logger
from backend.app.api import downloads, stats


# Global scheduler and sync service
scheduler = AsyncIOScheduler()
sync_service: SyncService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """
    global sync_service

    # Startup
    try:
        config = get_config()
    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        print("Please create config.yml from config.example.yml")
        raise
    except Exception as e:
        print(f"❌ ERROR loading config: {e}")
        raise

    # Initialize database
    try:
        await db.init_db()
    except Exception as e:
        print(f"❌ ERROR initializing database: {e}")
        raise

    # Initialize sync service
    sync_service = SyncService(config)

    # Inject sync_service into API modules
    downloads.sync_service = sync_service
    stats.sync_service = sync_service

    # Show startup banner
    logger.startup_banner(config)

    # Initial sync
    try:
        await sync_service.sync_downloads(fetch_media_info=False, is_initial=True)
    except Exception as e:
        print(f"{logger.timestamp()} ⚠️  Initial sync failed: {e}")
        print("           Will retry automatically every 5 seconds...")
        print()

    # Define async job functions
    async def sync_job():
        """Fast sync job - updates download status."""
        await sync_service.sync_downloads(fetch_media_info=False)

    async def poster_job():
        """Poster fetch job - gradually fetches missing posters."""
        await sync_service.fetch_missing_media_info()

    async def cleanup_job():
        """Cleanup job - removes old completed/failed downloads."""
        await sync_service.cleanup_old_downloads()

    # Schedule periodic jobs
    scheduler.add_job(
        sync_job,
        'interval',
        seconds=5,
        id='sync_downloads',
        max_instances=1
    )

    scheduler.add_job(
        poster_job,
        'interval',
        seconds=10,
        id='fetch_media_info',
        max_instances=1
    )

    scheduler.add_job(
        cleanup_job,
        'interval',
        minutes=config.cleanup.check_interval_minutes,
        id='cleanup_old_downloads',
        max_instances=1
    )

    scheduler.start()

    logger.separator()
    print(f"  ✅ Backend ready at http://{config.server.host}:{config.server.port}")
    print(f"  📖 API docs at http://{config.server.host}:{config.server.port}/docs")
    logger.separator()
    print()

    yield

    # Shutdown
    print(f"\n{logger.timestamp()} 🛑 Shutting down gracefully...")
    scheduler.shutdown()
    await db.close()


# Create FastAPI app
app = FastAPI(
    title="SABnzbd Media Tracker",
    description="Real-time web interface for monitoring SABnzbd downloads",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "SABnzbd Media Tracker API",
        "version": "2.0.0"
    }

# Include API routers
app.include_router(downloads.router)
app.include_router(stats.router)


if __name__ == "__main__":
    config = get_config()
    uvicorn.run(
        "backend.app.main:app",
        host=config.server.host,
        port=config.server.port,
        reload=True
    )
