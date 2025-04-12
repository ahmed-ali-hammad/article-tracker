import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models import Article, ArticleDetail


@pytest_asyncio.fixture
async def mock_get_async_db_session(mocker):
    session = mocker.MagicMock(spec=AsyncSession)
    yield session


@pytest_asyncio.fixture
async def mock_scheduler(mocker):
    scheduler = mocker.MagicMock()
    return scheduler


@pytest_asyncio.fixture
async def mock_article_repository(mocker):
    scheduler = mocker.AsyncMock()
    return scheduler


@pytest_asyncio.fixture
async def dummy_article():
    return Article(
        id=112,
        topline="Tech Giant Announces New Innovation",
        headline="Revolutionary Product Set to Transform the Industry",
        short_text="A global tech company unveils a game-changing product with innovative features, aiming to impact multiple sectors.",
        article_url="https://best.url",
    )


@pytest_asyncio.fixture
async def dummy_article_detail(dummy_article):
    return ArticleDetail(
        id=1,
        article_id=dummy_article.id,
        topline="Tech Giant Announces New Innovation",
        headline="Revolutionary Product Set to Transform the Industry",
        text=(
            "A global tech company unveils a game-changing product with innovative features, "
            "aiming to impact multiple sectors. Researchers have unveiled a new AI model that "
            "outperforms previous benchmarks in multiple domains."
        ),
        timestamp=1744454587,
    )
