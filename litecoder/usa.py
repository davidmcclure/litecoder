

import re
import pickle

from tqdm import tqdm
from collections import defaultdict
from itertools import product
from cached_property import cached_property
from box import Box

from sqlalchemy.inspection import inspect

from . import logger, US_CITY_PATH, US_STATE_PATH
from .models import WOFRegion, WOFLocality


# TODO: Country alt-names YAML.
USA_NAMES = (
    'USA',
    'United States',
    'United States of America',
    'US',
    'America',
)


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

        median_pop = WOFLocality.median_population()

        for row in tqdm(WOFLocality.query):
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


class CityKeyIter:

    def __init__(self, *args, **kwargs):
        self.allow_bare = AllowBareCityName(*args, **kwargs)

    def __call__(self, row):
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


def state_key_iter(row):
    """Enumerate index keys for a state.

    Args:
        row (db.Region)

    Yields: str
    """
    names = (row.name,)
    abbrs = (row.name_abbr,)

    # Name
    yield from names

    # TODO: Bare abbrs?

    # Name, USA
    for name, usa in product(names, USA_NAMES):
        yield ' '.join((name, usa))

    # Abbr, USA
    for abbr, usa in product(abbrs, USA_NAMES):
        yield ' '.join((abbr, usa))


class Match:

    def __init__(self, row):
        """Set model class, PK, metadata.
        """
        state = inspect(row)

        # Don't store the actual row, so we can serialize.
        self._model_cls = state.class_
        self._pk = state.identity

        self.data = Box(dict(row))

    @cached_property
    def db_row(self):
        """Hydrate database row, lazily.
        """
        return self._model_cls.query.get(self._pk)


class CityMatch(Match):

    def __repr__(self):
        return '%s<%s, %s, %s, wof:%d>' % (
            self.__class__.__name__,
            self.data.name,
            self.data.name_a1,
            self.data.name_a0,
            self.data.wof_id,
        )


class StateMatch(Match):

    def __repr__(self):
        return '%s<%s, %s, wof:%d>' % (
            self.__class__.__name__,
            self.data.name,
            self.data.name_a0,
            self.data.wof_id,
        )


class Index:

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as fh:
            return pickle.load(fh)

    def __init__(self):
        self._key_to_ids = defaultdict(set)
        self._id_to_loc = dict()

    def __len__(self):
        return len(self._key_to_ids)

    def __repr__(self):
        return '%s<%d keys, %d entities>' % (
            self.__class__.__name__,
            len(self._key_to_ids),
            len(self._id_to_loc),
        )

    def __getitem__(self, text):
        """Get ids, map to records.
        """
        ids = self._key_to_ids[keyify(text)]

        return [self._id_to_loc[id] for id in ids]

    def add_key(self, key, id):
        self._key_to_ids[key].add(id)

    def add_location(self, id, location):
        self._id_to_loc[id] = location

    def locations(self):
        return list(self._id_to_loc.values())

    def save(self, path):
        with open(path, 'wb') as fh:
            pickle.dump(self, fh)


class USCityIndex(Index):

    @classmethod
    def load(cls, path=US_CITY_PATH):
        return super().load(path)

    def build(self):
        """Index all US cities.
        """
        iter_keys = CityKeyIter()

        # Deduped cities.
        cities = WOFLocality.clean_us_cities()

        logger.info('Indexing US cities.')

        for row in tqdm(cities):

            # Key -> id(s)
            for key in map(keyify, iter_keys(row)):
                self.add_key(key, row.wof_id)

            # ID -> city
            self.add_location(row.wof_id, CityMatch(row))


class USStateIndex(Index):

    @classmethod
    def load(cls, path=US_STATE_PATH):
        return super().load(path)

    def build(self):
        """Index all US states.
        """
        states = WOFRegion.query.filter(WOFRegion.country_iso=='US')

        logger.info('Indexing US states.')

        for row in tqdm(states):

            # Key -> id(s)
            for key in map(keyify, state_key_iter(row)):
                self.add_key(key, row.wof_id)

            # ID -> state
            self.add_location(row.wof_id, StateMatch(row))
