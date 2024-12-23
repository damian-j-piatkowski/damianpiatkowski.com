import logging
from typing import List

from app.domain.log import Log
from app.extensions import db
from app.models.repositories.log_repository import LogRepository

logger = logging.getLogger(__name__)


def fetch_all_logs() -> List[Log]:
    """Service function to fetch all logs from the database.

    Returns:
        List[Log]: A list of Log domain objects.

    Raises:
        RuntimeError: If there is an error fetching the logs from the database.
    """
    session = db.session
    log_repo = LogRepository(session)
    try:
        logs = log_repo.fetch_all_logs()  # Fetch as Log objects
        return logs
    except RuntimeError as e:
        logger.error(f"Error in LogService: {e}")
        raise RuntimeError("Failed to retrieve log data") from e
