from flask_openapi3 import APIBlueprint, Tag
from src.api.schema import ArticleQuery, IntervalQuery
from src.db.main import get_async_db_session
from src.exceptions import ArticleNotFoundException
from src.log_utils import _logger
from src.scheduler import tagesschau_main_page_scheduler
from src.service import article_service

controller_bp = APIBlueprint("controller", __name__, url_prefix="/controller")
controller_tag = Tag(name="Controller", description=" ")


@controller_bp.post(
    "/crawl/overview-page/start",
    tags=[controller_tag],
    responses={
        200: {"description": "Crawler started successfully"},
        400: {"description": "Bad request: job not found"},
        500: {"description": "Internal server error"},
    },
)
async def trigger_crawl_now():
    """
    Immediately triggers the crawling process for the overview page.
    """
    try:
        crawl_triggered = await article_service.trigger_full_crawl_now(
            tagesschau_main_page_scheduler
        )
        if crawl_triggered:
            return {
                "status": "success",
                "message": "Crawler successfully triggered for the overview page.",
            }, 200
        return {"status": "error", "message": "Crawl job not found"}, 400
    except Exception as e:
        _logger.error(f"Error triggering crawl now: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while triggering the crawler.",
        }, 500


@controller_bp.post(
    "/crawl/single/article/start",
    tags=[controller_tag],
    responses={
        200: {"description": "Crawler started successfully"},
        400: {"description": "Bad request: article not found"},
        500: {"description": "Internal server error"},
    },
)
async def trigger_single_article_crawl(query: ArticleQuery):
    """
    Triggers the crawling process for a single article specified by its URL.
    """
    article_url = query.article_url
    try:
        async with get_async_db_session() as session:
            await article_service.trigger_single_article_crawl(
                session=session, article_url=article_url
            )
        return {
            "status": "success",
            "message": "Crawling started for the specified article.",
        }, 200
    except ArticleNotFoundException:
        return {"status": "error", "message": "Article not found"}, 400
    except Exception as e:
        _logger.error(
            f"Unexpected error while triggering crawl for article URL '{article_url}'. Error: {e}"
        )
        return {
            "status": "error",
            "message": "An internal error occurred while starting the crawl.",
        }, 500


@controller_bp.get(
    "/get/crawler/schedule/interval",
    tags=[controller_tag],
    responses={
        200: {"description": "Current scheduler interval in minutes"},
        500: {"description": "Internal server error"},
    },
)
async def get_crawler_schedule_interval():
    """
    Retrieves the current interval (in minutes) for the Tagesschau overview page crawler.
    """
    try:
        interval = await article_service.get_current_scheduler_interval(
            tagesschau_main_page_scheduler
        )
        return {
            "current_interval": interval,
            "unit": "minutes",
        }, 200
    except Exception as e:
        _logger.error(f"Error fetching scheduler interval: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while retrieving the interval.",
        }, 500


@controller_bp.put(
    "/change/crawler/schedule/interval",
    tags=[controller_tag],
    responses={
        200: {"description": "Interval updated"},
        400: {"description": "Invalid interval"},
        500: {"description": "Scheduler error"},
    },
)
async def change_crawler_schedule_interval(query: IntervalQuery):
    """
    Updates the execution interval (in minutes) for the overview page crawler.
    """
    try:
        minutes = query.minutes
        if minutes < 1:
            return {"message": "Interval must be at least 1 minute"}, 400

        interval_changed = await article_service.change_scheduler_interval(
            tagesschau_main_page_scheduler, minutes
        )

        if interval_changed:
            return {
                "status": "success",
                "message": f"Interval updated to {minutes} minutes.",
            }, 200

        return {"message": "Failed to update interval"}, 500
    except Exception as e:
        _logger.error(f"Error while updating scheduler interval: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while updating the interval.",
        }, 500


@controller_bp.get(
    "/get/crawler/status",
    tags=[controller_tag],
    responses={
        200: {"description": "Current job status"},
        500: {"description": "Internal server error"},
    },
)
async def get_scheduler_status():
    """
    Retrieves the current status of the overview page crawler scheduler.
    """
    try:
        status = await article_service.get_scheduler_status(
            tagesschau_main_page_scheduler
        )
        return status, 200
    except Exception as e:
        _logger.error(f"Error while getting scheduler status: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while retrieving the crawler status.",
        }, 500


@controller_bp.post(
    "/crawler/scheduler/enable",
    tags=[controller_tag],
    responses={
        200: {"description": "Crawler scheduler enabled"},
        500: {"description": "Scheduler error"},
    },
)
async def enable_scheduler():
    """
    Enables the scheduled job for the overview page crawler.
    """
    try:
        is_enabled = await article_service.enable_scheduler(
            tagesschau_main_page_scheduler
        )
        if is_enabled:
            return {"status": "success", "message": "Crawler scheduler enabled."}, 200

        return {
            "status": "error",
            "message": "Failed to enable the crawler scheduler.",
        }, 500
    except Exception as e:
        _logger.error(f"Error while enabling the scheduler: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while enabling the crawler scheduler.",
        }, 500


@controller_bp.post(
    "/crawler/scheduler/disable",
    tags=[controller_tag],
    responses={
        200: {"description": "Crawler scheduler disabled"},
        500: {"description": "Scheduler error"},
    },
)
async def disable_scheduler():
    """
    Disables the scheduled job for the overview page crawler.
    """
    try:
        is_disabled = await article_service.disable_scheduler(
            tagesschau_main_page_scheduler
        )
        if is_disabled:
            return {"status": "success", "message": "Crawler scheduler disabled."}, 200

        return {
            "status": "error",
            "message": "Failed to disable the crawler scheduler.",
        }, 500
    except Exception as e:
        _logger.error(f"Error while disabling the scheduler: {e}")
        return {
            "status": "error",
            "message": "An internal error occurred while disabling the crawler scheduler.",
        }, 500
