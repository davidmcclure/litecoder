

import us

from collections import defaultdict

from .db import City


class CityIndex(defaultdict):

    def __init__(self):
        """Index key -> city.
        """
        super().__init__(list)

        query = City.query.filter_by(country_code='US')

        for city in query:
            self[city.key()].append(city)


class StateIndex(dict):

    def __init__(self):
        """Index name -> state.
        """
        for state in us.STATES:

            self[state.abbr] = state
            self[state.name] = state

            self[state.abbr.lower()] = state
            self[state.name.lower()] = state


city_index = CityIndex()
state_index = StateIndex()
