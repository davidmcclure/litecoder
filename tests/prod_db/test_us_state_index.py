

import pytest

from litecoder.models import WOFRegion

from tests.utils import read_yaml


def yield_cases():
    """Generate cases from YAML file.
    """
    cases = read_yaml(__file__, 'test_us_state_index.yml')

    for group in cases:

        queries = group['query']

        if type(queries) is str:
            queries = [queries]

        for query in queries:
            yield query, group['matches']


@pytest.mark.parametrize('query,matches', yield_cases())
def test_cases(state_idx, query, matches):

    res = state_idx[query]

    ids = [r.data.wof_id for r in res]

    assert sorted(ids) == sorted(matches)


states = WOFRegion.query.filter(WOFRegion.country_iso=='US')


@pytest.mark.parametrize('state', states)
def test_all(state_idx, state):
    """Smoke test N most populous cities.
    """
    res = state_idx[state.name]
    res_ids = [r.data.wof_id for r in res]

    assert state.wof_id in res_ids
