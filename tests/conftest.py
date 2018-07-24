

import pytest

from litecoder.db import engine, session
from litecoder.models import BaseModel
from litecoder.sources.wof import WOFRegionRepo, WOFLocalityRepo
from litecoder.usa import USCityIndex, USStateIndex

from tests import REGION_DIR, LOCALITY_DIR


# TODO: Toggle between build disk db / testing mem db?
@pytest.fixture(scope='module')
def reset_db():
    """Drop and recreate the tables.
    """
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


@pytest.fixture(scope='module')
def load_db(reset_db):
    """Load tables.
    """
    WOFRegionRepo(REGION_DIR).load_db()
    WOFLocalityRepo(LOCALITY_DIR).load_db()


@pytest.fixture(scope='session')
def city_idx():
    return USCityIndex.load()


@pytest.fixture(scope='session')
def state_idx():
    return USStateIndex.load()
