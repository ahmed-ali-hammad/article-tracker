import asyncio
import logging
from datetime import datetime

from requests_html import AsyncHTMLSession, Element, HTMLResponse
from sqlalchemy.orm import Session
from src.db.main import get_async_db_session
from src.domain.service import ArticleService

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
_logger = logging.getLogger(__name__)

article_service = ArticleService()


class TagesschauCrawler:
    """
    A crawler for scraping articles from the Tagesschau website 'https://www.tagesschau.de/'.
    """

    def __init__(self, article_service: ArticleService, db_session: Session):
        """
        Initializes the TagesschauCrawler instance.

        Args:
            article_service (ArticleService): Service for managing article-related operations.
            db_session: The database session for interacting with the database.
        """
        self.async_request_html_session: AsyncHTMLSession | None = None
        self.article_service = article_service
        self.db_session = db_session

    async def initialize_async_request_html_session(self) -> None:
        """
        Initializes the async HTML session.
        """
        _logger.info("initializing AsyncHTMLSession instance.")
        if self.async_request_html_session is None:
            self.async_request_html_session = (
                await self.create_async_request_html_session()
            )

    @staticmethod
    async def create_async_request_html_session() -> AsyncHTMLSession:
        """
        Create a new AsyncHTMLSession instance.

        Returns:
            AsyncHTMLSession: A new instance used for making asynchronous HTML requests.
        """
        _logger.info("Creating a new AsyncHTMLSession instance.")
        return AsyncHTMLSession()

    async def run(self) -> None:
        """
        Entry point to run the crawler.
        """
        await self.initialize_async_request_html_session()
        articles = await self.fetch_article_sections("https://www.tagesschau.de/")
        await self.process_articles(articles=articles)

        _logger.info("Crawler run completed successfully.")

    async def fetch_article_sections(self, tagesschau_main_url: str) -> list:
        """
        Fetches the article sections from the Tagesschau main page.

        Args:
            tagesschau_main_url (str): URL of the Tagesschau homepage.

        Returns:
            list: A list of HTML elements representing grouped article sections.
        """
        _logger.info(f"Fetching main page article sections from {tagesschau_main_url}")
        tagesschau_main = await self.fetch_page(tagesschau_main_url)
        articles = tagesschau_main.html.find('[class="columns twelve teasergroup"]')
        return articles

    async def process_articles(self, articles: list) -> None:
        """
        Processes a list of articles by scraping full content and storing it in the database.

        For each article, it validates the article, saves it to the database, and fetches the full article content
        for further processing.

        Args:
            articles (list): A list of article teasers to be processed.
        """
        for index, teaser in enumerate(articles, start=1):
            _logger.info(f"Processing teaser article #{index}")

            try:
                topline = teaser.find(".teaser__topline", first=True)
                headline = teaser.find(".teaser__headline", first=True)
                short_text = teaser.find(".teaser__shorttext", first=True)
                article_url_set = teaser.find(".teaser__link", first=True)
                label = teaser.find(".teaser__label", first=True)

                is_article_valid = self.is_valid_article(
                    index=index,
                    topline=topline,
                    headline=headline,
                    short_text=short_text,
                    article_url_set=article_url_set,
                    label=label,
                )

                if not is_article_valid:
                    continue

                (url,) = article_url_set.absolute_links

                # saving the article
                _logger.info(
                    f"Saving article if it does not exist | Topline: '{topline.text}'."
                )

                article = await self.article_service.get_or_create_article(
                    session=self.db_session,
                    topline=topline.text,
                    headline=headline.text,
                    short_text=short_text.text,
                    article_url=url,
                )

                # process article detail
                await self.process_article_detail(url=url, article_id=article.id)

            except Exception as e:
                _logger.error(f"Error processing article {index}: {e}", exc_info=True)

        _logger.info("Finished processing all teaser articles.")

    async def fetch_page(self, url: str) -> HTMLResponse:
        """
        Fetch the HTML content of the specified URL using the async request session.

        Args:
            url (str): The URL to fetch.

        Returns:
            HTMLResponse: The response object containing the HTML content of the page.
        """
        _logger.info(f"Fetching URL: {url}")
        response = await self.async_request_html_session.get(url)
        _logger.info(f"Fetched URL: {url} with status code {response.status_code}")
        return response

    @staticmethod
    def is_valid_article(
        index: int,
        topline: Element,
        headline: Element,
        short_text: Element,
        article_url_set: set,
        label: Element,
    ) -> bool:
        """
        Validates whether an article should be processed.

        Args:
            index (int): The index of the article (for logging).
            topline, headline, short_text, link: Extracted elements of the article teaser.

        Returns:
            bool: True if the article is valid and should be processed, False otherwise.
        """
        if not (topline and headline and short_text and article_url_set):
            _logger.warning(f"Skipping article {index} – missing fields.")
            return False

        (url,) = article_url_set.absolute_links
        if not url.startswith("https://www.tagesschau.de/"):
            _logger.info(f"Skipping article {index} – not a news link.")
            return False

        if label and label.text in ["Bilder"]:
            _logger.info(f"Skipping article {index} – only pictures.")
            return False

        if topline.text in ["Spenden", "Wettervorhersage Deutschland", "lotto"]:
            _logger.info(f"Skipping article {index} – filtered by topline.")
            return False

        return True

    async def process_article_detail(self, url: str, article_id: int) -> None:
        """
        Fetches and parses the article detail page, then stores the article detail in the database.

        Args:
            url (str): URL of the full article.
            article_id (int): ID of the corresponding article in the DB.
        """
        detail_page = await self.fetch_page(url)

        datetime_element = detail_page.html.find(
            ".metatextline, .multimediahead__date", first=True
        )
        paragraphs = detail_page.html.find("p.textabsatz")
        topline = detail_page.html.find(".seitenkopf__topline", first=True)
        headline = detail_page.html.find(".seitenkopf__headline--text", first=True)

        timestamp = await self.convert_datetime_to_epoch(datetime_element.text)
        full_text = "\n".join(p.text for p in paragraphs)

        _logger.info(
            f"Saving article_detail if it does not exist | for article_id: {article_id} | Topline: '{topline.text}'."
        )

        await self.article_service.get_or_create_article_detail(
            session=self.db_session,
            article_id=article_id,
            topline=topline.text,
            headline=headline.text,
            text=full_text,
            timestamp=timestamp,
        )

    @staticmethod
    async def convert_datetime_to_epoch(datetime_str: str) -> int:
        """
        Converts a datetime string in the format 'Stand: dd.mm.yyyy hh:mm Uhr' to epoch time.

        This function takes a datetime string, removes unwanted parts, and converts the remaining
        datetime to an epoch timestamp.

        Args:
            datetime_str (str): The datetime_str string to be converted.
            expected in the format 'Stand: dd.mm.yyyy hh:mm Uhr'.

        Returns:
            int: The corresponding epoch timestamp.

        Example:
            >>> convert_datetime_to_epoch('Stand: 04.04.2025 16:10 Uhr')
            1680615000
        """
        # Remove unwanted parts from the date string
        cleaned_date_str = datetime_str.replace("Stand: ", "").replace(" Uhr", "")

        # Define the date format
        date_format = "%d.%m.%Y %H:%M"

        # Convert the string to a datetime object
        date_obj = datetime.strptime(cleaned_date_str, date_format)

        # Convert the datetime object to epoch time
        epoch_time = int(date_obj.timestamp())

        return epoch_time


if __name__ == "__main__":

    async def main():
        async with get_async_db_session() as session:
            tagesschau_crawler = TagesschauCrawler(
                article_service=article_service, db_session=session
            )
            await tagesschau_crawler.run()

    asyncio.run(main())
