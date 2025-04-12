import pytest
from requests.exceptions import MissingSchema
from src.db.models import ArticleDetail
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

        mock_article_repository.get_article_by_url.return_value = dummy_article
        mock_crawler = mocker.patch("src.service.run_single_tagesschau_article_crawler")

        await article_service.trigger_single_article_crawl(
            session=mock_get_async_db_session,
            article_url=dummy_article.article_url,
            article_repository=mock_article_repository,
        )

        mock_article_repository.get_article_by_url.assert_called_once_with(
            session=mock_get_async_db_session, article_url=dummy_article.article_url
        )
        mock_crawler.assert_called_once_with(
            article_id=dummy_article.id, article_url=dummy_article.article_url
        )

    @pytest.mark.asyncio
    async def test_trigger_single_article_crawl_article_not_found(
        self, mocker, mock_get_async_db_session, mock_article_repository, dummy_article
    ):

        mock_article_repository.get_article_by_url.return_value = None
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
        mock_article_repository.get_article_by_url.side_effect = Exception(
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

    @pytest.mark.asyncio
    async def test_update_scheduler_interval_success(self, mock_scheduler):
        minutes = 5
        mock_scheduler.update_interval.return_value = True
        result = await article_service.update_scheduler_interval(
            scheduler=mock_scheduler, minutes=minutes
        )

        assert result is True
        mock_scheduler.update_interval.assert_called_once_with(minutes)

    @pytest.mark.asyncio
    async def test_update_scheduler_interval_value_error(self, mock_scheduler):
        minutes = -100
        mock_scheduler.update_interval.side_effect = ValueError(
            "Interval must be a positive number of minutes."
        )

        with pytest.raises(
            ValueError, match="Interval must be a positive number of minutes."
        ):
            await article_service.update_scheduler_interval(
                scheduler=mock_scheduler, minutes=minutes
            )

        mock_scheduler.update_interval.assert_called_once_with(minutes)

    @pytest.mark.asyncio
    async def test_update_scheduler_interval_job_not_found(self, mock_scheduler):
        minutes = 5
        mock_scheduler.update_interval.return_value = False
        result = await article_service.update_scheduler_interval(
            scheduler=mock_scheduler, minutes=minutes
        )

        assert result is False
        mock_scheduler.update_interval.assert_called_once_with(minutes)

    @pytest.mark.asyncio
    async def test_update_scheduler_interval_unexpected_exception(self, mock_scheduler):
        minutes = 5
        mock_scheduler.update_interval.side_effect = RuntimeError(
            "Something went wrong"
        )

        with pytest.raises(RuntimeError, match="Something went wrong"):
            await article_service.update_scheduler_interval(
                scheduler=mock_scheduler, minutes=minutes
            )

        mock_scheduler.update_interval.assert_called_once_with(minutes)

    @pytest.mark.asyncio
    async def test_update_scheduler_interval_invalid_type(self, mock_scheduler):
        minutes = "five"
        mock_scheduler.update_interval.side_effect = TypeError(
            "TypeError: '<' not supported between instances of 'str' and 'int'"
        )

        with pytest.raises(
            TypeError,
            match="TypeError: '<' not supported between instances of 'str' and 'int'",
        ):
            await article_service.update_scheduler_interval(
                scheduler=mock_scheduler, minutes=minutes
            )

        mock_scheduler.update_interval.assert_called_once_with(minutes)

    @pytest.mark.asyncio
    async def test_get_scheduler_status_success(self, mock_scheduler):

        mock_scheduler.job_status.return_value = {
            "enabled": True,
            "interval": "3 minutes",
            "running": True,
        }

        status = await article_service.get_scheduler_status(mock_scheduler)

        assert status is not None
        assert isinstance(status, dict)
        mock_scheduler.job_status.assert_called_once()

        assert status == {
            "enabled": True,
            "interval": "3 minutes",
            "running": True,
        }

    @pytest.mark.asyncio
    async def test_get_scheduler_status_unexpected_exception(self, mock_scheduler):

        mock_scheduler.job_status.side_effect = RuntimeError("Something went wrong")

        with pytest.raises(RuntimeError, match="Something went wrong"):
            await article_service.get_scheduler_status(mock_scheduler)

        mock_scheduler.job_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_enable_scheduler_success(self, mock_scheduler):
        mock_scheduler.enable_job.return_value = True
        result = await article_service.enable_scheduler(mock_scheduler)

        assert isinstance(result, bool)
        assert result is True
        mock_scheduler.enable_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_enable_scheduler_job_not_found(self, mock_scheduler):
        mock_scheduler.enable_job.return_value = False
        result = await article_service.enable_scheduler(mock_scheduler)

        assert isinstance(result, bool)
        assert result is False
        mock_scheduler.enable_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_enable_scheduler_unexpected_exception(self, mock_scheduler):

        mock_scheduler.enable_job.side_effect = RuntimeError("Something went wrong")

        with pytest.raises(RuntimeError, match="Something went wrong"):
            await article_service.enable_scheduler(mock_scheduler)

        mock_scheduler.enable_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_scheduler_success(self, mock_scheduler):
        mock_scheduler.disable_job.return_value = True
        result = await article_service.disable_scheduler(mock_scheduler)

        assert isinstance(result, bool)
        assert result is True
        mock_scheduler.disable_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_scheduler_job_not_found(self, mock_scheduler):
        mock_scheduler.disable_job.return_value = False
        result = await article_service.disable_scheduler(mock_scheduler)

        assert isinstance(result, bool)
        assert result is False
        mock_scheduler.disable_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_disable_scheduler_unexpected_exception(self, mock_scheduler):

        mock_scheduler.disable_job.side_effect = RuntimeError("Something went wrong")

        with pytest.raises(RuntimeError, match="Something went wrong"):
            await article_service.disable_scheduler(mock_scheduler)

        mock_scheduler.disable_job.assert_called_once()

    @pytest.mark.asyncio
    async def test_retrieve_all_articles_success(
        self, mock_get_async_db_session, mock_article_repository, dummy_article
    ):
        mock_article_repository.get_all_articles.return_value = [dummy_article]

        articles = await article_service.retrieve_all_articles(
            mock_get_async_db_session, mock_article_repository
        )

        assert articles is not None
        assert isinstance(articles, list)
        assert articles[0] == dummy_article
        mock_article_repository.get_all_articles.assert_called_with(
            mock_get_async_db_session
        )

    @pytest.mark.asyncio
    async def test_retrieve_all_articles_empty_response(
        self, mock_get_async_db_session, mock_article_repository
    ):
        mock_article_repository.get_all_articles.return_value = []

        articles = await article_service.retrieve_all_articles(
            mock_get_async_db_session, mock_article_repository
        )

        assert articles is not None
        assert isinstance(articles, list)
        assert len(articles) == 0
        mock_article_repository.get_all_articles.assert_called_with(
            mock_get_async_db_session
        )

    @pytest.mark.asyncio
    async def test_retrieve_all_articles_database_error(
        self, mock_get_async_db_session, mock_article_repository
    ):
        mock_article_repository.get_all_articles.side_effect = Exception(
            "Database Error"
        )

        with pytest.raises(Exception, match="Database Error"):
            await article_service.retrieve_all_articles(
                mock_get_async_db_session, mock_article_repository
            )

        mock_article_repository.get_all_articles.assert_called_with(
            mock_get_async_db_session
        )

    @pytest.mark.asyncio
    async def test_retrieve_article_by_id_success(
        self, mock_get_async_db_session, mock_article_repository, dummy_article_detail
    ):
        mock_article_repository.get_article_detail_by_id.return_value = (
            dummy_article_detail
        )

        article_detail = await article_service.retrieve_article_by_id(
            mock_get_async_db_session, 1, mock_article_repository
        )

        assert article_detail is not None
        assert isinstance(article_detail, ArticleDetail)
        assert article_detail == dummy_article_detail
        mock_article_repository.get_article_detail_by_id.assert_called_with(
            mock_get_async_db_session, 1
        )

    @pytest.mark.asyncio
    async def test_retrieve_article_by_id_none(
        self, mock_get_async_db_session, mock_article_repository
    ):
        mock_article_repository.get_article_detail_by_id.return_value = None

        article_detail = await article_service.retrieve_article_by_id(
            mock_get_async_db_session, 1, mock_article_repository
        )

        assert article_detail is None
        mock_article_repository.get_article_detail_by_id.assert_called_with(
            mock_get_async_db_session, 1
        )

    @pytest.mark.asyncio
    async def test_retrieve_article_by_id_database_error(
        self, mock_get_async_db_session, mock_article_repository
    ):
        mock_article_repository.get_article_detail_by_id.side_effect = Exception(
            "Database Error"
        )

        with pytest.raises(Exception, match="Database Error"):
            await article_service.retrieve_article_by_id(
                mock_get_async_db_session, 1, mock_article_repository
            )

        mock_article_repository.get_article_detail_by_id.assert_called_with(
            mock_get_async_db_session, 1
        )

    @pytest.mark.asyncio
    async def test_search_articles_by_keyword_success(
        self, mock_get_async_db_session, mock_article_repository, dummy_article_detail
    ):

        mock_article_repository.search_article_details_by_keyword.return_value = [
            dummy_article_detail
        ]

        articles_detail = await article_service.search_articles_by_keyword(
            mock_get_async_db_session, "game-changing", mock_article_repository
        )

        assert articles_detail is not None
        assert isinstance(articles_detail, list)
        assert articles_detail[0] == dummy_article_detail
        mock_article_repository.search_article_details_by_keyword.assert_called_with(
            mock_get_async_db_session, "game-changing"
        )

    @pytest.mark.asyncio
    async def test_search_articles_by_keyword_not_found(
        self, mock_get_async_db_session, mock_article_repository
    ):

        mock_article_repository.search_article_details_by_keyword.return_value = []

        articles_detail = await article_service.search_articles_by_keyword(
            mock_get_async_db_session, "Not-Found-keyword", mock_article_repository
        )

        assert articles_detail is not None
        assert isinstance(articles_detail, list)
        assert len(articles_detail) == 0
        mock_article_repository.search_article_details_by_keyword.assert_called_with(
            mock_get_async_db_session, "Not-Found-keyword"
        )

    @pytest.mark.asyncio
    async def test_search_articles_by_keyword_database_error(
        self, mock_get_async_db_session, mock_article_repository
    ):

        mock_article_repository.search_article_details_by_keyword.side_effect = (
            Exception("Database Error")
        )

        with pytest.raises(Exception, match="Database Error"):
            await article_service.search_articles_by_keyword(
                mock_get_async_db_session, "Not-Found-keyword", mock_article_repository
            )

        mock_article_repository.search_article_details_by_keyword.assert_called_with(
            mock_get_async_db_session, "Not-Found-keyword"
        )
