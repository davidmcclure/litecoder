

import re

from tqdm import tqdm
from collections import defaultdict
from itertools import product

from . import logger
from .models import Region


USA_NAMES = (
    'USA',
    'United States',
    'United States of America',
    'US',
    'America',
)


# TODO: Test
def keyify(text):
    """Convert text -> normalized index key.
    """
    text = text.lower()
    text = text.strip()

    text = text.replace('.', '')
    text = re.sub('[,-]', ' ', text)
    text = re.sub('\s{2,}', ' ', text)

    return text


class USStateKeyIter:

    def _iter_keys(self, row):
        """Enumerate index keys for a state.

        Args:
            row (db.Region)

        Yields: str
        """
        names = (row.name,)
        abbrs = (row.name_abbr,)

        # Name
        yield from names

        # Abbr
        yield from abbrs

        # Name, USA
        for name, usa in product(names, USA_NAMES):
            yield ' '.join((name, usa))

        # Abbr, USA
        for abbr, usa in product(abbrs, USA_NAMES):
            yield ' '.join((abbr, usa))

    def __call__(self, row):
        for text in self._iter_keys(row):
            yield keyify(text)


class USStateIndex:

    def __init__(self):
        self._idx = defaultdict(set)

    def __len__(self):
        return len(self._idx)

    def __repr__(self):
        return '%s<%d keys>' % (self.__class__.__name__, len(self))

    def __getitem__(self, text):
        return self._idx[keyify(text)]

    def build(self):
        """Index all US states.
        """
        iter_keys = USStateKeyIter()

        states = Region.query.filter(Region.country_iso=='US')

        logger.info('Indexing US states.')

        for row in tqdm(states):

            # Generate keys, ensure no errors.
            keys = list(iter_keys(row))

            # Index complete key set.
            for key in keys:
                self[key].add(row.wof_id)

    def query(self, text):
        """Get ids, query database records.
        """
        ids = self[text]

        # TODO: Preload db rows?
        return (
            Region.query.filter(Region.wof_id.in_(ids)).all()
            if ids else []
        )
