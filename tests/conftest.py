

import pytest

from litecoder.db import engine
from litecoder.models import BaseModel


@pytest.fixture(scope='session', autouse=True)
def init_testing_db():
    """Drop and recreate the tables.
    """
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


@pytest.yield_fixture
def db():
    """Reset the testing database.
    """
    session.begin_nested()
    yield
    session.remove()
