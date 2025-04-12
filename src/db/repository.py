from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.db.models import Article, ArticleDetail


class ArticleRepository:
    """
    A class for handling db operations related to articles and their details.
    """

    @staticmethod
    async def get_all_articles(session: AsyncSession) -> list[Article]:
        """
        Retrieves all articles from the database, including their associated article details.

        This method uses `selectinload` to perform a JOIN on the `ArticleDetail` table
        in the same query, fetching the related article details for each article.

        Args:
            session (AsyncSession): The SQLAlchemy async session to use for querying.

        Returns:
            list[Article]: A list of all `Article` objects, each including its related `ArticleDetail` records.
        """
        statement = select(Article).options(selectinload(Article.details))
        result = await session.execute(statement)
        articles = result.scalars().all()
        return articles

    @staticmethod
    async def get_article_by_url(
        session: AsyncSession, article_url: str
    ) -> Article | None:
        """
        Get an article by its URL.

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
        article = await ArticleRepository.get_article_by_url(
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

        # Reload the object from the database to ensure auto-generated fields (ID) are available.
        await session.refresh(new_article)
        return new_article

    @staticmethod
    async def get_article_detail_by_article_id_and_timestamp(
        session: AsyncSession, article_id: int, timestamp: int
    ) -> ArticleDetail | None:
        """
        Get an article_detail by article_id and timestamp.

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
    async def get_article_detail_by_id(
        session: AsyncSession, article_detail_id: int
    ) -> ArticleDetail | None:
        """
        Find article_detail by article_detail_id.

        Args:
            session (AsyncSession): The asynchronous database session.
            article_detail_id (int): the id of the article_detail.

        Returns:
            ArticleDetail | None: The found article detail object, or None if not found.
        """
        statement = select(ArticleDetail).where(ArticleDetail.id == article_detail_id)
        result = await session.execute(statement)
        article_detail = result.scalar_one_or_none()
        return article_detail

    @staticmethod
    async def search_article_details_by_keyword(
        session: AsyncSession, keyword: str
    ) -> list[ArticleDetail]:
        """
        Searches for articles_detail containing a given keyword.
        it returns only the latest version (highest ID) for each article.

        This query uses PostgreSQL's `DISTINCT ON` strategy to ensure that only the
        most recent ArticleDetail (based on ID) per `article_id` is returned when
        the keyword appears in any of the searchable fields.

        Args:
            session (AsyncSession): The SQLAlchemy async session to use.
            keyword (str): The search term to match in the topline, headline, or text.

        Returns:
            list[ArticleDetail]: A list of the latest matching ArticleDetail records.

        SQL equivalent:
            SELECT DISTINCT ON (article_id) *
            FROM article_detail
            WHERE
                topline ILIKE '%keyword%' OR
                headline ILIKE '%keyword%' OR
                text ILIKE '%keyword%'
            ORDER BY article_id, id DESC;
        """
        statement = (
            select(ArticleDetail)
            .distinct(ArticleDetail.article_id)
            .where(
                or_(
                    ArticleDetail.topline.ilike(f"%{keyword}%"),
                    ArticleDetail.headline.ilike(f"%{keyword}%"),
                    ArticleDetail.text.ilike(f"%{keyword}%"),
                )
            )
            .order_by(ArticleDetail.article_id, ArticleDetail.id.desc())
        )

        result = await session.execute(statement)
        return result.scalars().all()

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
        article_detail = (
            await ArticleRepository.get_article_detail_by_article_id_and_timestamp(
                session=session, article_id=article_id, timestamp=timestamp
            )
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

        # Reload the object from the database to ensure auto-generated fields (ID) are available.
        await session.refresh(new_article_detail)
        return new_article_detail


article_repository = ArticleRepository()
