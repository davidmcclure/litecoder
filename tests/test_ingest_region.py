

import pytest
import os

from litecoder.models import Region

from tests.utils import read_yaml


pytestmark = pytest.mark.usefixtures('load_db')


cases = read_yaml(__file__, 'test_ingest_region.yml')


@pytest.mark.parametrize('wof_id,fields', cases.items())
def test_test(wof_id, fields):

    row = Region.query.get(wof_id)

    for col, val in fields.items():
        assert getattr(row, col) == val
