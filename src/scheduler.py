import asyncio
from datetime import datetime
from threading import Thread

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.crawler import run_full_tagesschau_crawler
from src.log_utils import _logger


class CrawlerScheduler:
    def __init__(self, job_id):
        self.job_id = job_id
        self.current_interval = 60  # An Hour
        self.scheduler = None
        self.loop = None
        self.thread = None
        self.enabled = True

    def start(self):
        """Start the scheduler in a background thread"""

        def _run_scheduler():
            # Creating a new asyncio event loop, so it doesn't interfere with the main thread's loop (Flask App)
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Creating an AsyncIOScheduler and binding it to the newly created event loop
            self.scheduler = AsyncIOScheduler(event_loop=self.loop)
            self.scheduler.add_job(
                run_full_tagesschau_crawler,
                "interval",
                minutes=self.current_interval,
                id=self.job_id,
            )
            self.scheduler.start()
            try:
                # Starting the event loop and keeping it running forever
                # This is necessary to keep the scheduler alive
                self.loop.run_forever()
            except (KeyboardInterrupt, SystemExit):
                # Graceful shutdown if the app is stopped
                pass

        # Runing the scheduler setup and event loop in a separate daemon thread
        # This allows the main thread (Flask App) to continue running
        self.thread = Thread(target=_run_scheduler, daemon=True)

        # Start the background thread
        self.thread.start()

    def is_running(self):
        """Checks if the scheduler exists and is currently running"""
        return self.scheduler and self.scheduler.running

    def trigger_now(self):
        """Trigger the crawler immediately"""
        if not self.is_running():
            _logger.warning("Scheduler not running. Starting scheduler...")
            self.start()

        job = self.scheduler.get_job(self.job_id)

        if job:
            # Found the job – trigger it
            _logger.info(f"Executing crawler job '{self.job_id}' ahead of schedule.")
            job.modify(next_run_time=datetime.now())
            return True
        else:
            # Job wasn't found – can't trigger it
            _logger.warning(
                f"Failed to trigger crawler job: Job ID '{self.job_id}' not found."
            )
            return False

    def update_interval(self, minutes: int):
        """Update the interval for the scheduled job"""
        if not self.is_running():
            _logger.info("Scheduler not running. Starting scheduler...")
            self.start()

        if minutes <= 0:
            raise ValueError("Interval must be a positive number of minutes.")

        job = self.scheduler.get_job(self.job_id)
        if job:
            _logger.info(
                f"Rescheduling job '{self.job_id}': interval changed from {self.current_interval} to {minutes} minutes."
            )
            self.scheduler.reschedule_job(
                self.job_id, trigger=IntervalTrigger(minutes=minutes)
            )
            self.current_interval = minutes
            return True
        else:
            _logger.warning(
                f"Unable to update interval: job '{self.job_id}' not found in scheduler."
            )
            return False

    def enable_job(self):
        """Enable (resume) the scheduled job"""
        if not self.is_running():
            self.start()

        job = self.scheduler.get_job(self.job_id)
        if job:
            job.resume()
            self.enabled = True
            _logger.info(f"Job '{self.job_id}' has been enabled.")
            return True
        else:
            _logger.warning(f"Failed to enable job: job '{self.job_id}' not found.")
            return False

    def disable_job(self):
        """Disable (pause) the scheduled job"""
        if not self.is_running():
            return False

        job = self.scheduler.get_job(self.job_id)
        if job:
            job.pause()
            self.enabled = False
            _logger.info(f"Job '{self.job_id}' has been disabled (paused).")
            return True
        else:
            _logger.warning(f"Failed to disable job: job '{self.job_id}' not found.")
            return False

    def job_status(self):
        """Get current job status"""
        status = {
            "enabled": self.enabled,
            "interval": f"{self.current_interval} minutes",
            "running": self.is_running(),
        }
        _logger.info(f"job: {self.job_id} - status: {status}")
        return status

    def stop(self):
        """Stop the scheduler gracefully"""
        if self.scheduler:
            _logger.info("Shutting down the scheduler...")
            self.scheduler.shutdown()

            # Stop the event loop gracefully
            self.loop.call_soon_threadsafe(self.loop.stop)

            # waiting for the background thread to finish
            self.thread.join()
        else:
            _logger.warning("Scheduler is not running. No shutdown required.")


tagesschau_main_page_scheduler = CrawlerScheduler(job_id="tagesschau_main_page_crawler")
