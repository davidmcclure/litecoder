

import us
import re

from cached_property import cached_property
from boltons.iterutils import windowed


def tokenize_toponym(text):
    return re.findall('[a-z-\.]+', text, re.I)


class StateIndex(dict):

    def __init__(self):
        """Index name -> state.
        """
        for state in us.STATES:
            self[state.abbr.lower()] = state
            self[state.name.lower()] = state


class ToponymTokens(list):

    @classmethod
    def from_text(cls, text):
        """Tokenize a raw string.
        """
        return cls(re.findall('[a-z-\.]+', text, re.I))

    @cached_property
    def key(self):
        """Make an index key.
        """
        return ' '.join([t.lower() for t in self])

    def ngrams(self, maxn=4):
        """Generate all ngrams.
        """
        for n in range(1, max(maxn+1, len(self))):
            yield from map(self.__class__, windowed(self, n))


class LocationFieldText(str):

    @cached_property
    def parts(self):
        """Split comma-delimited parts.
        """
        return [p.strip() for p in self.split(',')]

    @cached_property
    def part_tokens(self):
        """Tokenize parts.

        Returns: list of ToponymTokens
        """
        return list(map(ToponymTokens.from_text, self.parts))

    def ngrams(self, *args, **kwargs):
        """Generate all ngrams inside of parts.
        """
        for tokens in self.part_tokens:
            yield from tokens.ngrams(*args, **kwargs)

    def keys(self, *args, **kwargs):
        """Generate index keys.
        """
        for ng in self.ngrams(*args, **kwargs):
            yield ng.key


def usa_city_state(query):
    """Given a raw location field, try to extract a US city and/or state.

    Args:
        query (str)

    Returns: litecoder.db.City|None, us.states.State|None
    """
    pass
