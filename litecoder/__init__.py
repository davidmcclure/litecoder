

import us

from cached_property import cached_property


class StateIndex(dict):

    def __init__(self):
        """Index name -> state.
        """
        for state in us.STATES:
            self[state.abbr.lower()] = state
            self[state.name.lower()] = state


class FreetextLocation(str):

    @cached_property
    def parts(self):
        """Split comma-delimited parts.
        """
        return [p.strip() for p in self.split(',')]

    @cached_property
    def lower_parts(self):
        """Lowercased parts.
        """
        return list(map(str.lower, self.parts))


def usa_city_state(query):
    """Given a raw location field, try to extract a US city and/or state.

    Args:
        query (str)

    Returns: litecoder.db.City|None, us.states.State|None
    """
    pass
