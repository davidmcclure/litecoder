

import pytest

from litecoder.usa import USCityIndex

from tests.utils import read_yaml


def yield_cases():
    """Generate cases from YAML file.
    """
    cases = read_yaml(__file__, 'test_us_city_index.yml')

    for group in cases:

        queries = group['query']

        if type(queries) is str:
            queries = [queries]

        for query in queries:
            yield query, group['matches']


@pytest.mark.parametrize('query,matches', yield_cases())
def test_us_city_index(city_idx, query, matches):

    res = city_idx[query]

    ids = [r.wof_id for r in res]

    assert sorted(ids) == sorted(matches)
