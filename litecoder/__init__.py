

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
            states.append((ngram, state))

        for city in City.lookup(ngram.key(), 'US'):
            cities.append((ngram, city))

    print(cities, states)
