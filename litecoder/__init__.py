

import pandas as pd

from .db import state_index, City
from .parsers import LocationField


class Matches:

    def __init__(self):
        self.cities = []
        self.states = []

    def add_city(self, city):
        self.cities.append(city)

    def add_state(self, state):
        self.states.append(state)

    def max_city_key_len(self):
        """Get size of the longest city index key.
        """
        key_lens = [len(c.key()) for c in self.cities]

        return max(key_lens) if key_lens else 0

    def max_len_cities(self):
        """Generate cities with longest keys.
        """
        max_len = self.max_city_key_len()

        for city in self.cities:
            if len(city.key()) == max_len:
                yield city

    def pop_ranked_cities(self):
        """Order city candidates by population.
        """
        return sorted(
            self.max_len_cities(),
            key=lambda c: c.population,
            reverse=True,
        )

    def state_abbrs(self):
        return set([s.abbr for s in self.states])

    def city_state(self, min_pop_ratio = 3):
        """Extract city and/or state.
        """
        res_city, res_state = None, None

        cities = self.pop_ranked_cities()

        # 1 city, 0 states.
        if len(cities) == 1 and len(self.states) == 0:
            res_city = cities[0]

        # 1 state, 0 cities.
        elif len(self.states) == 1 and len(cities) == 0:
            res_state = self.states[0]

        # 2+ cities, 1+ states - look for city / state pair.
        elif cities and self.states:

            state_abbrs = self.state_abbrs()

            for city in cities:
                if city.admin1_code in state_abbrs:
                    res_city = city
                    break

        # 2+ cities, no state - take highest-pop city, if the population is X
        # times greater than the second-largest match.
        elif len(cities) > 1 and not self.states:

            pop_ratio = cities[0].population / cities[1].population

            if pop_ratio > min_pop_ratio:
                res_city = cities[0]

        # Get state for matched city.
        if res_city:
            res_state = state_index[res_city.admin1_code]

        return res_city, res_state


def twitter_usa_city_state(text):
    """Given a Twitter location text, match to a city and/or state.
    """
    field = LocationField.from_text(text)

    matches = Matches()

    # Get candidates.
    for ngram in field.candidate_toponyms():

        state = state_index.get(ngram.key())

        if state:
            matches.add_state(state)

        # Skip cities with same names as states.
        else:
            for city in City.lookup(ngram.key(), 'US'):
                matches.add_city(city)

    return matches.city_state()
