import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text
from src.config import Config

_logger = logging.getLogger(__name__)


engine = create_async_engine(Config.ASYNC_DATABASE_URI, echo=False)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)


@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession]:
    """
    Initializes an asynchronous database session using SQLAlchemy's
    async engine and sessionmaker. It yields an `AsyncSession` instance, which can
    be used to interact with the database. The session is automatically closed
    after usage.

    Returns:
        AsyncSession: database session
    """
    async with async_session() as session:
        yield session


def check_db_connection(session) -> bool:
    """
    Simple check for database connection using a SELECT query.

    Args:
        session: The database session.

    Returns:
        bool: True if the DB is reachable, False otherwise.
    """
    try:
        session.execute(text("SELECT 1"))
        return True
    except Exception as e:
        _logger.error(f"Database connection error: {e}")
        return False
