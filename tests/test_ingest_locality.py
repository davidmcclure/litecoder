

import pytest
import os

from litecoder.models import Locality

from tests.utils import read_yaml


pytestmark = pytest.mark.usefixtures('load_db')


cases = read_yaml(__file__, 'test_ingest_locality.yml')


@pytest.mark.parametrize('wof_id,fields', cases.items())
def test_test(wof_id, fields):

    row = Locality.query.get(wof_id)
    print(row)

    for col, val in fields.items():
        assert getattr(row, col) == val
