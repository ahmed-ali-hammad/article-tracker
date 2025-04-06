import asyncio
from datetime import datetime
from threading import Thread

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.crawler import run_full_tagesschau_crawler
from src.log_utils import _logger


class CrawlerScheduler:
    def __init__(self, job_id):
        self.scheduler = None
        self.loop = None
        self.thread = None
        self.job_id = job_id
        self.current_interval = 1
        self.enabled = True

    def start(self):
        """Start the scheduler in a background thread"""

        def run_scheduler():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            self.scheduler = AsyncIOScheduler(event_loop=self.loop)
            self.scheduler.add_job(
                run_full_tagesschau_crawler, "interval", minutes=1, id=self.job_id
            )
            self.scheduler.start()
            try:
                self.loop.run_forever()
            except (KeyboardInterrupt, SystemExit):
                pass

        self.thread = Thread(target=run_scheduler, daemon=True)
        self.thread.start()

    def is_running(self):
        return self.scheduler and self.scheduler.running

    def trigger_now(
        self,
    ):
        """Trigger the crawler immediately"""
        if not self.is_running():
            _logger.info("Scheduler not running - starting it first")
            self.start()

        # Get the job and run it immediately
        job = self.scheduler.get_job(self.job_id)

        if job:
            _logger.info("Manually triggering crawler job")
            job.modify(next_run_time=datetime.now())
            return True
        return False

    def update_interval(self, minutes: int):
        """Update the job interval"""
        if not self.is_running():
            _logger.info("Scheduler not running - starting it first")
            self.start()

        if minutes <= 0:
            raise ValueError("Interval must be positive")

        job = self.scheduler.get_job(self.job_id)
        if job:
            _logger.info(
                f"Updating interval from {self.current_interval} to {minutes} minutes"
            )
            self.scheduler.reschedule_job(
                self.job_id, trigger=IntervalTrigger(minutes=minutes)
            )
            self.current_interval = minutes
            return True
        return False

    def enable_job(self):
        """Enable the scheduled job"""
        if not self.is_running():
            self.start()

        job = self.scheduler.get_job(self.job_id)
        if job:
            job.resume()
            self.enabled = True
            _logger.info("Scheduled job enabled")
            return True
        return False

    def disable_job(self):
        """Disable the scheduled job"""
        if not self.is_running():
            return False

        job = self.scheduler.get_job(self.job_id)
        if job:
            job.pause()
            self.enabled = False
            _logger.info("Scheduled job disabled")
            return True
        return False

    def job_status(self):
        """Get current job status"""
        return {
            "enabled": self.enabled,
            "interval": f"{self.current_interval} minutes",
            "running": self.is_running(),
        }

    def stop(self):
        """Stop the scheduler gracefully"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.loop.call_soon_threadsafe(self.loop.stop)
            self.thread.join()
            self.scheduler = None
            self.loop = None


tagesschau_main_page_scheduler = CrawlerScheduler(job_id="tagesschau_main_page_crawler")
