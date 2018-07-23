

import pytest

from litecoder.db import engine, session
from litecoder.models import BaseModel
from litecoder.sources import WOFRegionRepo, WOFLocalityRepo
from litecoder.usa import USCityIndex

from tests import REGION_DIR, LOCALITY_DIR


@pytest.fixture(scope='session', autouse=True)
def init_testing_db():
    """Drop and recreate the tables.
    """
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


@pytest.yield_fixture(scope='module')
def db():
    """Reset the testing database.
    """
    session.begin_nested()
    yield
    session.remove()


@pytest.fixture(scope='module')
def load_db(db):
    """Load tables.
    """
    WOFRegionRepo(REGION_DIR).load_db()
    WOFLocalityRepo(LOCALITY_DIR).load_db()


@pytest.fixture(scope='session')
def city_idx():
    return USCityIndex.load()
