

import pytest

from litecoder import twitter_usa_city_state


@pytest.mark.parametrize('query,city_id,state_abbr', [
    ('Alabama', None, 'AL'),
])
def test_twitter_usa_city_state(query, city_id, state_abbr):

    city, state = twitter_usa_city_state(query)

    if city_id:
        assert city.geonameid == city_id
        assert state.abbr == city.admin1_code

    elif state_abbr:
        assert city is None
        assert state.abbr == state_abbr

    else:
        assert city is None
        assert state is None
