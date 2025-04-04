import logging

from sqlalchemy.sql import text

_logger = logging.getLogger(__name__)


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
