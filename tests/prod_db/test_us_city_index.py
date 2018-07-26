

import pytest

from litecoder.models import WOFLocality

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
def test_cases(city_idx, query, matches, xfail):

    if xfail:
        pytest.xfail()

    res = city_idx[query]

    ids = [r.data.wof_id for r in res]

    # Exact id list match.
    assert sorted(ids) == sorted(matches)


topn = (WOFLocality.clean_query()
    .filter(WOFLocality.country_iso=='US')
    .filter(WOFLocality.name != None)
    .filter(WOFLocality.name_a1 != None)
    .order_by(WOFLocality.population.desc())
    .limit(1000))


@pytest.mark.parametrize('city', topn)
def test_topn(city_idx, city):
    """Smoke test N most populous cities.
    """
    res = city_idx['%s, %s' % (city.name, city.name_a1)]
    res_ids = [r.data.wof_id for r in res]

    assert city.wof_id in res_ids
