

import pandas as pd

from .db import CityIndex
from .parsers import StateIndex, LocationFieldText


state_index = StateIndex()


def usa_city_state(query):
    """Given a raw location field, try to extract a US city and/or state.

    Args:
        query (str)

    Returns: litecoder.db.City|None, us.states.State|None
    """
    query = LocationFieldText(query)

    keys = list(query.keys())

    states = pd.DataFrame([
        dict(key=k, state=state_index[k])
        for k in keys if k in state_index
    ])

    cities = pd.DataFrame([
        dict(key=k, population=c.city.population, city=c.city)
        for c in matches for matches in CityIndex.lookup()
    ])

    cities = []
    for key in keys:
        cities += CityIndex.lookup(key)
