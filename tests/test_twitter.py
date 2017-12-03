

import pytest

from litecoder import geocode_twitter

from tests.utils import read_yaml


def yield_cases():
    """Generate cases from YAML file.
    """
    cases = read_yaml(__file__, 'twitter.yml')

    for group in cases:

        queries = group['query']

        if type(queries) is str:
            queries = [queries]

        for query in queries:
            yield query, group.get('city'), group.get('state')


@pytest.mark.parametrize('query,city_id,state_abbr', yield_cases())
def test_twitter_usa_city_state(query, city_id, state_abbr):

    city, state = geocode_twitter(query)

    if city_id:
        assert city.geonameid == city_id
        assert state.abbr == city.admin1_code

    elif state_abbr:
        assert city is None
        assert state.abbr == state_abbr

    else:
        assert city is None
        assert state is None
