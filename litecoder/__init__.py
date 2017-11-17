

import pandas as pd

from .db import state_index, City
from .parsers import LocationField


def twitter_usa_city_state(text):
    """Given a Twitter location text, match to a city and/or state.
    """
    field = LocationField.from_text(text)

    # Get candidates.
    states = []
    cities = []
    for ngram in field.candidate_toponyms():

        state = state_index.get(ngram.key())

        if state:
            states.append(state)

        for city in City.lookup(ngram.key(), 'US'):
            cities.append(city)

    abbr_to_state = {s.abbr: s for s in states}

    # Sort cities by length of name first, then population.
    cities = sorted(
        cities,
        key=lambda c: (len(c.name), c.population),
        reverse=True
    )

    city, state = None, None

    # if len(cities) == 1 and len(states) == 0:
        # city = cities[0]
        # state = state_index[city.admin1_code]

    # elif len(cities) == 0 and len(states) == 1:
        # state = states[0]

    # Cities, no state - take first city.
    if cities and not states:
        city = cities[0]
        state = state_index[city.admin1_code]

    # State, no cities - take state.
    elif len(states) == 1 and not cities:
        state = states[0]

    # Take first city with matching state.
    else:
        for city_ in cities:
            state_ = abbr_to_state.get(city_.admin1_code)
            if state_:
                city, state = city_, state_
                break

    return city, state
