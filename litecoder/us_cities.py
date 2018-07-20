

import re
import pickle

from tqdm import tqdm
from collections import defaultdict
from itertools import product

from . import logger
from .models import City


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


class NamePopulations(defaultdict):

    def __init__(self):
        """Index name -> [pops], using median pop if no metadata.
        """
        super().__init__(list)

        logger.info('Indexing name -> populations.')

        median_pop = City.median_population()

        for city in tqdm(City.query):
            for name in city.names:
                self[keyify(name)].append(city.population or median_pop)

    def __getitem__(self, text):
        return super().__getitem__(keyify(text))


class AllowBareName:

    def __init__(self, min_p2_ratio=10):
        self.name_pops = NamePopulations()
        self.min_p2_ratio = min_p2_ratio

    def __call__(self, city, name):
        """Is a city name unique enough that it should be indexed
        independently?

        Args:
            city (models.City)
            name (str)

        Returns: bool
        """
        all_pops = sorted(self.name_pops[name], reverse=True)

        if len(all_pops) < 2:
            return True

        p2_ratio = (city.population or 0) / all_pops[1]

        if p2_ratio > self.min_p2_ratio:
            return True

        return False


class USCityKeyIter:

    def __init__(self, *args, **kwargs):
        self.allow_bare = AllowBareName(*args, **kwargs)

    def _iter_keys(self, city):
        """Enumerate index keys for a city.

        Args:
            city (db.City)

        Yields: str
        """
        bare_names = [n for n in city.names if self.allow_bare(city, n)]

        states = (city.name_a1, city.us_state_abbr)

        for name in bare_names:
            yield name

        for name, usa in product(bare_names, USA_NAMES):
            yield ' '.join((name, usa))

        for name, state in product(city.names, states):
            yield ' '.join((name, state))

        for name, state, usa in product(city.names, states, USA_NAMES):
            yield ' '.join((name, state, usa))

    def __call__(self, city):
        for text in self._iter_keys(city):
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

        cities = City.query.filter(City.country_iso=='US')

        logger.info('Indexing US cities.')

        for city in tqdm(cities):

            try:

                # Generate keys, ensure no errors.
                keys = list(iter_keys(city))

                # Index complete key set.
                for key in iter_keys(city):
                    self[key].add(city.wof_id)

            except Exception as e:
                pass

    def save(self, path):
        with open(path, 'wb') as fh:
            pickle.dump(self._idx, fh)

    def load(self, path):
        with open(path, 'rb') as fh:
            self._idx = pickle.load(fh)

    def query(self, text):
        """Get ids, query database records.
        """
        ids = self[text]

        return (
            City.query.filter(City.wof_id.in_(ids)).all()
            if ids else []
        )
