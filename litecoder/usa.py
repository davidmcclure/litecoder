

import re
import pickle

from tqdm import tqdm
from collections import defaultdict
from itertools import product

from . import logger
from .models import Locality, Region


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


class CityNamePopulations(defaultdict):

    def __init__(self):
        """Index name -> [pops], using median pop if no metadata.
        """
        super().__init__(list)

        logger.info('Indexing name -> populations.')

        median_pop = Locality.median_population()

        for row in tqdm(Locality.query):
            for name in row.names:
                self[keyify(name)].append(row.population or median_pop)

    def __getitem__(self, text):
        return super().__getitem__(keyify(text))


class AllowBareCityName:

    def __init__(self, min_p1_gap=200000):
        self.name_pops = CityNamePopulations()
        self.min_p1_gap = min_p1_gap

    def __call__(self, row, name):
        """Is a city name unique enough that it should be indexed
        independently?

        Args:
            row (models.Locality)
            name (str)

        Returns: bool
        """
        all_pops = sorted(self.name_pops[name], reverse=True)

        pop = row.population or 0

        return pop - sum(all_pops[1:]) > self.min_p1_gap


class USCityKeyIter:

    def __init__(self, *args, **kwargs):
        self.allow_bare = AllowBareCityName(*args, **kwargs)

    def _iter_keys(self, row):
        """Enumerate index keys for a city.

        Args:
            row (db.Locality)

        Yields: str
        """
        bare_names = [n for n in row.names if self.allow_bare(row, n)]

        # Get non-empty state names.
        state_names = [n for n in (row.name_a1, row.us_state_abbr) if n]

        # Bare name
        for name in bare_names:
            yield name

        # Bare name, USA
        for name, usa in product(bare_names, USA_NAMES):
            yield ' '.join((name, usa))

        # Name, state
        for name, state in product(row.names, state_names):
            yield ' '.join((name, state))

        # Name, state, USA
        for name, state, usa in product(row.names, state_names, USA_NAMES):
            yield ' '.join((name, state, usa))

    def __call__(self, row):
        for text in self._iter_keys(row):
            yield keyify(text)


# Just function, with @keyify decorator?
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

        # TODO: ?
        # Abbr
        # yield from abbrs

        # Name, USA
        for name, usa in product(names, USA_NAMES):
            yield ' '.join((name, usa))

        # Abbr, USA
        for abbr, usa in product(abbrs, USA_NAMES):
            yield ' '.join((abbr, usa))

    def __call__(self, row):
        for text in self._iter_keys(row):
            yield keyify(text)


class USCityIndex:

    def __init__(self):
        self._idx = defaultdict(set)

    def __len__(self):
        return len(self._idx)

    def __repr__(self):
        return '%s<%d keys>' % (self.__class__.__name__, len(self))

    def __getitem__(self, text):
        return self._idx[keyify(text)]

    def build(self):
        """Index all US cities.
        """
        iter_keys = USCityKeyIter()

        cities = Locality.query.filter(Locality.country_iso=='US')

        logger.info('Indexing US cities.')

        for row in tqdm(cities):

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
            Locality.query.filter(Locality.wof_id.in_(ids)).all()
            if ids else []
        )


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
