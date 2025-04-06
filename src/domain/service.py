from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Article, ArticleDetail


class ArticleService:
    """
    A service class for handling operations related to articles and their details.
    """

    @staticmethod
    async def find_article_by_url(
        session: AsyncSession, article_url: str
    ) -> Article | None:
        """
        Find an article by its URL.

        Args:
            session (AsyncSession): The asynchronous database session.
            article_url (str): The URL of the article to search for.

        Returns:
            Article | None: The found article object, or None if not found.
        """
        statement = select(Article).where(Article.article_url == article_url)
        result = await session.execute(statement)
        article = result.scalar_one_or_none()
        return article

    @staticmethod
    async def get_or_create_article(
        session: AsyncSession,
        topline: str,
        headline: str,
        short_text: str,
        article_url: str,
    ) -> Article:
        """
        Retrieve an existing article by its URL or create a new article if it doesn't exist.

        Args:
            session (AsyncSession): The asynchronous database session.
            topline (str): The topline of the article.
            headline (str): The headline of the article.
            short_text (str): The short text of the article.
            article_url (str): The URL of the article.

        Returns:
            Article: The existing or newly created article.
        """
        article = await ArticleService.find_article_by_url(
            session=session, article_url=article_url
        )
        if article:
            return article

        new_article = Article(
            topline=topline,
            headline=headline,
            short_text=short_text,
            article_url=article_url,
        )
        session.add(new_article)
        await session.commit()
        return new_article

    @staticmethod
    async def find_article_detail(
        session: AsyncSession, article_id: int, timestamp: int
    ) -> ArticleDetail | None:
        """
        Find article_detail by article_id and timestamp.

        Args:
            session (AsyncSession): The asynchronous database session.
            article_id (int): the article_id associated with this article_detail.
            timestamp (int): The timestamp of the article detail to search for.

        Returns:
            ArticleDetail | None: The found article detail object, or None if not found.
        """
        statement = select(ArticleDetail).where(
            ArticleDetail.article_id == article_id, ArticleDetail.timestamp == timestamp
        )
        result = await session.execute(statement)
        article_detail = result.scalar_one_or_none()
        return article_detail

    @staticmethod
    async def get_or_create_article_detail(
        session: AsyncSession,
        article_id: int,
        topline: str,
        headline: str,
        text: str,
        timestamp: int,
    ) -> ArticleDetail:
        """
        Retrieve an existing article detail by its article_id and timestamp or create
        a new article detail if it doesn't exist.

        Args:
            session (AsyncSession): The asynchronous database session.
            article_id (int): The ID of the article associated with this article detail.
            topline (str): The topline of the article detail.
            headline (str): The headline of the article detail.
            text (str): The text content of the article detail.
            timestamp (int): The timestamp of the article detail.

        Returns:
            ArticleDetail: The existing or newly created article detail.
        """
        article_detail = await ArticleService.find_article_detail(
            session=session, article_id=article_id, timestamp=timestamp
        )
        if article_detail:
            return article_detail

        new_article_detail = ArticleDetail(
            article_id=article_id,
            topline=topline,
            headline=headline,
            text=text,
            timestamp=timestamp,
        )
        session.add(new_article_detail)
        await session.commit()

        return new_article_detail
