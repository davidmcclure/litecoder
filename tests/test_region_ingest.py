

import pytest
import os

from litecoder.sources import WOFRegionRepo, WOFLocalityRepo
from litecoder.models import Region

from tests import REGION_DIR, LOCALITY_DIR
from tests.utils import read_yaml


cases = read_yaml(__file__, 'regions.yml')


@pytest.fixture(scope='module', autouse=True)
def ingest(db):
    WOFRegionRepo(REGION_DIR).load_db()
    WOFLocalityRepo(LOCALITY_DIR).load_db()


def test_test():
    print(Region.query.count())
    assert True
