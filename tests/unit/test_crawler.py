import pytest
from requests_html import AsyncHTMLSession


class TestTagesschauCrawler:
    @pytest.mark.asyncio
    async def test_initialize_async_request_html_session_success(
        self, tagesschau_crawler_fixture
    ):
        await tagesschau_crawler_fixture.initialize_async_request_html_session()
        async_request_html_session = (
            tagesschau_crawler_fixture.async_request_html_session
        )

        assert async_request_html_session is not None
        assert isinstance(async_request_html_session, AsyncHTMLSession)

    @pytest.mark.asyncio
    async def test_initialize_called_twice_uses_same_session(
        self, tagesschau_crawler_fixture
    ):
        await tagesschau_crawler_fixture.initialize_async_request_html_session()
        first_session = tagesschau_crawler_fixture.async_request_html_session

        await tagesschau_crawler_fixture.initialize_async_request_html_session()
        second_session = tagesschau_crawler_fixture.async_request_html_session

        assert first_session is second_session

    @pytest.mark.asyncio
    async def test_initialize_does_not_reinitialize_if_exists(
        self, tagesschau_crawler_fixture
    ):
        mock_html_session = AsyncHTMLSession()
        tagesschau_crawler_fixture.async_request_html_session = mock_html_session

        await tagesschau_crawler_fixture.initialize_async_request_html_session()

        assert (
            tagesschau_crawler_fixture.async_request_html_session is mock_html_session
        )

    @pytest.mark.asyncio
    async def test_create_async_request_html_session_success(
        self, mocker, tagesschau_crawler_fixture
    ):
        mock_session = mocker.patch("src.crawler.AsyncHTMLSession")
        mock_session.return_value = AsyncHTMLSession()

        html_session = (
            await tagesschau_crawler_fixture.create_async_request_html_session()
        )

        assert html_session is not None
        assert isinstance(html_session, AsyncHTMLSession)
        mock_session.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_async_request_html_session_failure(
        self, mocker, tagesschau_crawler_fixture
    ):
        mocker.patch(
            "src.crawler.AsyncHTMLSession",
            side_effect=Exception("Session creation failed"),
        )

        with pytest.raises(Exception, match="Session creation failed"):
            await tagesschau_crawler_fixture.create_async_request_html_session()

    @pytest.mark.asyncio
    async def test_run_success(self, mocker, tagesschau_crawler_fixture, dummy_article):

        mock_fetch_article_sections = mocker.patch(
            "src.crawler.TagesschauCrawler.fetch_article_sections",
            return_value=[dummy_article],
        )

        mock_process_articles = mocker.patch(
            "src.crawler.TagesschauCrawler.process_articles",
        )

        await tagesschau_crawler_fixture.run()

        mock_fetch_article_sections.assert_awaited_once_with(
            "https://www.tagesschau.de/"
        )

        mock_process_articles.assert_awaited_once_with(articles=[dummy_article])

    @pytest.mark.asyncio
    async def test_run_with_no_articles(self, mocker, tagesschau_crawler_fixture):
        mock_fetch_article_sections = mocker.patch(
            "src.crawler.TagesschauCrawler.fetch_article_sections",
            return_value=[],
        )
        mock_process_articles = mocker.patch(
            "src.crawler.TagesschauCrawler.process_articles"
        )

        await tagesschau_crawler_fixture.run()

        mock_fetch_article_sections.assert_awaited_once_with(
            "https://www.tagesschau.de/"
        )

        mock_process_articles.assert_awaited_once_with(articles=[])

    import pytest

    @pytest.mark.asyncio
    async def test_run_fetch_article_sections_raises(
        self, mocker, tagesschau_crawler_fixture
    ):
        mocker.patch(
            "src.crawler.TagesschauCrawler.fetch_article_sections",
            side_effect=Exception("fetch failed"),
        )

        with pytest.raises(Exception, match="fetch failed"):
            await tagesschau_crawler_fixture.run()

    @pytest.mark.asyncio
    async def test_run_process_articles_raises(
        self, mocker, tagesschau_crawler_fixture, dummy_article
    ):
        mocker.patch(
            "src.crawler.TagesschauCrawler.fetch_article_sections",
            return_value=[dummy_article],
        )

        mocker.patch(
            "src.crawler.TagesschauCrawler.process_articles",
            side_effect=Exception("processing failed"),
        )

        with pytest.raises(Exception, match="processing failed"):
            await tagesschau_crawler_fixture.run()
