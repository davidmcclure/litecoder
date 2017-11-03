

import us


class StateIndex(dict):

    def __init__(self):
        """Index name -> state.
        """
        for state in us.STATES:
            self[state.abbr.lower()] = state
            self[state.name.lower()] = state


def usa_city_state(query):
    """Given a raw location field, try to extract a US city and/or state.

    Args:
        query (str)

    Returns: litecoder.db.City|None, us.states.State|None
    """
    pass
