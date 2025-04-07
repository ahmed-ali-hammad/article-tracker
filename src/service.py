from sqlalchemy.ext.asyncio import AsyncSession
from src.crawler import run_single_tagesschau_article_crawler
from src.db.models import Article, ArticleDetail
from src.db.repository import article_repository
from src.exceptions import ArticleNotFoundException
from src.scheduler import CrawlerScheduler


class ArticleService:
    @staticmethod
    async def trigger_full_crawl_now(scheduler: CrawlerScheduler) -> bool:
        """
        Immediately triggers the full crawl job via the scheduler.

        Args:
            scheduler: The scheduler instance managing the overview page job.

        Returns:
            bool: True if the crawl was successfully triggered, False otherwise.
        """
        if scheduler.trigger_now():
            return True
        return False

    @staticmethod
    async def trigger_single_article_crawl(
        session: AsyncSession, article_url: str
    ) -> None:
        """
        Triggers crawling for a single article by its URL.

        Args:
            session (AsyncSession): The database session used to fetch the article.
            article_url (str): The URL of the article to crawl.

        Raises:
            ArticleNotFoundException: If the article is not found in the database.
        """
        article = await article_repository.find_article_by_url(
            session=session, article_url=article_url
        )

        if article is None:
            raise ArticleNotFoundException
        await run_single_tagesschau_article_crawler(
            article_id=article.id, article_url=article_url
        )

    @staticmethod
    async def get_current_scheduler_interval(scheduler: CrawlerScheduler) -> int:
        """
        Retrieves the current scheduler interval in minutes.

        Args:
            scheduler: The scheduler instance.

        Returns:
            int: The current interval in minutes.
        """
        return scheduler.current_interval

    @staticmethod
    async def change_scheduler_interval(
        scheduler: CrawlerScheduler, minutes: int
    ) -> bool:
        """
        Updates the scheduler interval.

        Args:
            scheduler: The scheduler instance.
            minutes (int): The new interval in minutes.

        Returns:
            bool: True if the interval was updated successfully, False otherwise.
        """
        return scheduler.update_interval(minutes)

    @staticmethod
    async def get_scheduler_status(scheduler: CrawlerScheduler) -> dict:
        """
        Retrieves the current status of the scheduler.

        Args:
            scheduler: The scheduler instance.

        Returns:
            dict: The scheduler status.
        """
        return scheduler.job_status()

    @staticmethod
    async def enable_scheduler(scheduler: CrawlerScheduler) -> bool:
        """
        Enables the scheduled job in the scheduler.

        Args:
            scheduler: The scheduler instance.

        Returns:
            bool: True if the job was enabled successfully, False otherwise.
        """
        return scheduler.enable_job()

    @staticmethod
    async def disable_scheduler(scheduler: CrawlerScheduler) -> bool:
        """
        Disables the scheduled job in the scheduler.

        Args:
            scheduler: The scheduler instance.

        Returns:
            bool: True if the job was disabled successfully, False otherwise.
        """
        return scheduler.disable_job()

    @staticmethod
    async def fetch_all_articles(session: AsyncSession) -> list[Article]:
        """
        This method retrieves a list of all articles stored in the database.

        Args:
            session (AsyncSession): The SQLAlchemy async session to use for querying.

        Returns:
            list[Article]: A list of all `Article` objects from the database.
        """
        return await article_repository.get_all_articles(session)

    @staticmethod
    async def fetch_article_detail(
        session: AsyncSession, article_detail_id: int
    ) -> ArticleDetail | None:
        """
        Fetches the article detail for the given article_detail_id.

        This method retrieves a single `ArticleDetail` based on the provided
        `article_detail_id`.

        Args:
            session (AsyncSession): The SQLAlchemy async session to use for querying.
            article_detail_id (int): The ID of the article detail to fetch.

        Returns:
            ArticleDetail | None: The matching `ArticleDetail` if found, otherwise None.
        """
        return await article_repository.find_article_detail_by_id(
            session, article_detail_id
        )

    @staticmethod
    async def search_articles(session: AsyncSession, keyword: str) -> list[Article]:
        """
        Searches for the latest version of articles containing the given keyword.
        This method delegates to the repository to find article details that match a keyword.

        We're currently performing the search using SQL queries,
        which is not the most optimal solution.
        A more efficient approach would be to use a tool like Elasticsearch,
        which is specifically designed for fast, scalable full-text search and indexing.

        Args:
            session (AsyncSession): The active SQLAlchemy async session.
            keyword (str): The keyword to search for.

        Returns:
            list[Article]: A list of Article instances with matching details.
        """
        return await article_repository.find_article_detail_by_keyword(session, keyword)


article_service = ArticleService()
