

import re
import os
import hashlib
import struct
from sqlitedict import SqliteDict
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

    def __init__(self, min_p1_gap=200000, blocklist=None):
        self.name_pops = CityNamePopulations()
        self.min_p1_gap = min_p1_gap
        self.blocklist = set(map(keyify, blocklist or []))

    def blocked(self, name):
        return keyify(name) in self.blocklist

    def large_p1_gap(self, row, name):
        """Get the difference in population between this city and the second-
        most-populous city with the name. Allow if over threshold.
        """
        all_pops = sorted(self.name_pops[name], reverse=True)
        pop = row.population or 0
        return pop - sum(all_pops[1:]) > self.min_p1_gap

    def __call__(self, row, name):
        """Is a name unique enough that it should be indexed independently?

        Args:
            row (models.WOFLocality)
            name (str)

        Returns: bool
        """
        return not self.blocked(name) and self.large_p1_gap(row, name)


class CityKeyIter:

    def __init__(self, allow_bare):
        self.allow_bare = allow_bare

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

    # Now that loading the database is instantenous, it is better to put it in the constructor over a
    #   separate load method
    # @classmethod
    # def load(cls, path):
    #     with open(path, 'rb') as fh:
    #         return pickle.load(fh)

    def __init__(self, path):
        self._key_to_ids = SqliteDict(filename=path, tablename="keys")
        self._id_to_loc = SqliteDict(filename=path, tablename="locations")

    def __len__(self):
        return len(self._key_to_ids)

    def __repr__(self):
        return '%s<%d keys, %d entities>' % (
            self.__class__.__name__,
            len(self._key_to_ids),
            len(self._id_to_loc),
        )

    def __getitem__(self, key):
        """Get ids, map to records only if there is a match in the index
        """
        # convert string to integer
        hash = hashlib.md5(bytes(keyify(key), encoding="utf-8")).digest()
        hashed_key = struct.unpack("L", hash[:8])[0] % (2 ** 63)
        if hashed_key not in self._key_to_ids:
            return None

        ids = self._key_to_ids[hashed_key]

        return [self._id_to_loc[id] for id in ids]

    def add_key(self, key, id):
        # convert string to integer
        hash = hashlib.md5(bytes(key, encoding="utf-8")).digest()
        hashed_key = struct.unpack("L", hash[:8])[0] % (2 ** 63)
        if hashed_key not in self._key_to_ids:
            self._key_to_ids[hashed_key] = set()
        curr_ids = self._key_to_ids[hashed_key]
        curr_ids.add(id)
        self._key_to_ids[hashed_key] = curr_ids
        self._key_to_ids.commit()
        del curr_ids

    def add_location(self, id, location):
        self._id_to_loc[id] = location
        self._id_to_loc.commit()

    def locations(self):
        return list(self._id_to_loc.values())

    def close(self):
        self._key_to_ids.close()
        self._id_to_loc.close()


class USCityIndex(Index):

    def __init__(self, bare_name_blocklist=None):
        super().__init__(path=US_CITY_PATH)
        self.bare_name_blocklist = bare_name_blocklist

    def build(self):
        """Index all US cities.
        """
        allow_bare = AllowBareCityName(blocklist=self.bare_name_blocklist)

        iter_keys = CityKeyIter(allow_bare)

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

    def __init__(self):
        super().__init__(path=US_STATE_PATH)

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