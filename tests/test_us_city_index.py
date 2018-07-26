

import pytest

from tests.utils import read_yaml


def yield_cases():
    """Generate cases from YAML file.
    """
    cases = read_yaml(__file__, 'test_us_city_index.yml')

    for group in cases:

        queries = group['query']

        xfail = group.get('xfail', False)

        if type(queries) is str:
            queries = [queries]

        for query in queries:
            yield query, group['matches'], xfail


@pytest.mark.parametrize('query,matches,xfail', yield_cases())
def test_us_city_index(city_idx, query, matches, xfail):

    if xfail:
        pytest.xfail()

    res = city_idx[query]

    ids = [r.data.wof_id for r in res]

    # Exact id list match.
    assert sorted(ids) == sorted(matches)
