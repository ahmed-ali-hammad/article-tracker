import asyncio
import atexit

from flask import jsonify
from flask_openapi3 import Info, OpenAPI, Tag
from src.api.routers.controller import controller_bp
from src.api.routers.explorer import explorer_bp
from src.config import Config
from src.db.main import check_db_connection, dispose_db_engine, get_async_db_session
from src.log_utils import _logger
from src.scheduler import tagesschau_main_page_scheduler


def run_cleanup_tasks():
    """
    Executes the necessary tasks when the application is shutting down.
    """
    _logger.info("Application is shutting down, starting cleanup tasks...")

    tagesschau_main_page_scheduler.stop()
    asyncio.run(dispose_db_engine())

    _logger.info("Cleanup tasks completed successfully.")


# This register the cleanup function to run at shutdown
atexit.register(run_cleanup_tasks)


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    info = Info(title="Article Tracker", version="1.0.0")
    app = OpenAPI(__name__, info=info)

    app.config.from_object(config_class)

    app.register_api(controller_bp)
    app.register_api(explorer_bp)

    @app.get(
        "/health", tags=[Tag(name="Health", description="API health status endpoint")]
    )
    async def health():
        """Check the health status of the API."""
        async with get_async_db_session() as session:
            if not await check_db_connection(session):
                return jsonify("API is unavailable"), 500
        return jsonify("API is healthy"), 200

    # Start scheduler for the crawler
    if not tagesschau_main_page_scheduler.is_running():
        tagesschau_main_page_scheduler.start()

    return app
