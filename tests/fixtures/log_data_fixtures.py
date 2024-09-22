from typing import Callable

import pytest
from sqlalchemy.orm import Session

from app.domain.log import Log


@pytest.fixture(scope='function')
def create_log(session: Session) -> Callable[..., Log]:
    """Fixture to create a Log instance (commit happens in the test)."""

    def _create_log(
            level='INFO',
            message='Test log message'
    ) -> Log:
        log_entry = Log(
            level=level,
            message=message
        )
        session.add(log_entry)
        return log_entry  # Commit responsibility is moved to the test

    return _create_log
