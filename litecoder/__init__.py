

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

    print(keys)
