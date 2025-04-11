import pytest
from requests.exceptions import MissingSchema
from src.exceptions import ArticleNotFoundException
from src.service import article_service


class TestArticleService:
    @pytest.mark.asyncio
    async def test_trigger_full_crawl_now_success(self, mock_scheduler):
        mock_scheduler.trigger_now.return_value = True
        result = await article_service.trigger_full_crawl_now(scheduler=mock_scheduler)

        assert result is True
        mock_scheduler.trigger_now.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_full_crawl_now_scheduler_failure(self, mock_scheduler):
        mock_scheduler.trigger_now.return_value = False
        result = await article_service.trigger_full_crawl_now(scheduler=mock_scheduler)

        assert result is False

    @pytest.mark.asyncio
    async def test_trigger_full_crawl_now_with_none_scheduler(self):
        with pytest.raises(AttributeError):
            await article_service.trigger_full_crawl_now(scheduler=None)

    @pytest.mark.asyncio
    async def test_trigger_full_crawl_now_trigger_raises(self, mock_scheduler):
        mock_scheduler.trigger_now.side_effect = RuntimeError(
            "The scheduler is on a lunch break"
        )

        with pytest.raises(RuntimeError):
            await article_service.trigger_full_crawl_now(scheduler=mock_scheduler)

    @pytest.mark.asyncio
    async def test_trigger_single_article_crawl_success(
        self, mocker, mock_get_async_db_session, mock_article_repository, dummy_article
    ):

        mock_article_repository.find_article_by_url.return_value = dummy_article
        mock_crawler = mocker.patch("src.service.run_single_tagesschau_article_crawler")

        await article_service.trigger_single_article_crawl(
            session=mock_get_async_db_session,
            article_url=dummy_article.article_url,
            article_repository=mock_article_repository,
        )

        mock_article_repository.find_article_by_url.assert_called_once_with(
            session=mock_get_async_db_session, article_url=dummy_article.article_url
        )
        mock_crawler.assert_called_once_with(
            article_id=dummy_article.id, article_url=dummy_article.article_url
        )

    @pytest.mark.asyncio
    async def test_trigger_single_article_crawl_article_not_found(
        self, mocker, mock_get_async_db_session, mock_article_repository, dummy_article
    ):

        mock_article_repository.find_article_by_url.return_value = None
        mock_crawler = mocker.patch("src.service.run_single_tagesschau_article_crawler")

        with pytest.raises(ArticleNotFoundException):
            await article_service.trigger_single_article_crawl(
                session=mock_get_async_db_session,
                article_url=dummy_article.article_url,
                article_repository=mock_article_repository,
            )

        mock_crawler.assert_not_called()

    @pytest.mark.asyncio
    async def test_trigger_single_article_crawl_empty_url(
        self, mock_get_async_db_session, mock_article_repository
    ):

        with pytest.raises(MissingSchema):
            await article_service.trigger_single_article_crawl(
                session=mock_get_async_db_session,
                article_url="",
                article_repository=mock_article_repository,
            )

    @pytest.mark.asyncio
    async def test_trigger_single_article_crawl_unexpected_error(
        self, mock_get_async_db_session, mock_article_repository
    ):
        mock_article_repository.find_article_by_url.side_effect = Exception(
            "Unexpected error"
        )

        with pytest.raises(Exception):
            await article_service.trigger_single_article_crawl(
                session=mock_get_async_db_session,
                article_url="https://best.url",
                article_repository=mock_article_repository,
            )

    @pytest.mark.asyncio
    async def test_get_current_scheduler_interval_success(self, mock_scheduler):
        mock_scheduler.current_interval = 10
        interval = await article_service.get_current_scheduler_interval(mock_scheduler)

        assert interval == 10

    @pytest.mark.asyncio
    async def test_get_current_scheduler_interval_with_none_scheduler(self):
        with pytest.raises(AttributeError):
            await article_service.get_current_scheduler_interval(None)

    @pytest.mark.asyncio
    async def test_get_current_scheduler_interval_none_value(mock_scheduler):
        mock_scheduler.current_interval = None

        interval = await article_service.get_current_scheduler_interval(mock_scheduler)

        assert interval is None
