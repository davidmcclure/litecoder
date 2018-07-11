

import attr
import os
import csv
import us
import ujson
import re
import logging
import sys

from boltons.iterutils import chunked_iter
from tqdm import tqdm
from collections import defaultdict, UserDict
from itertools import product
from glob import iglob

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float


logging.basicConfig(
    format='%(asctime)s | %(levelname)s : %(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)

logger = logging.getLogger('geovec')


def make_key(text, lower=True):
    """Normalize text string -> index key.
    """
    text = text.strip()
    text = re.sub('\s{2,}', ' ', text)

    if lower:
        text = text.lower()

    return text


def safe_get(d, key, *keys):
    """Safe nested dict lookup.
    """
    if keys:
        return safe_get(d.get(key, {}), *keys)

    return d.get(key)


def safe_get_first(d, paths):
    """Return first match.
    """
    for path in paths:
        val = safe_get(d, *path)
        if val:
            return val


# TODO: Config-ify
db_path = os.path.join(os.path.dirname(__file__), 'litecoder.db')

url = URL(drivername='sqlite', database=db_path)
engine = create_engine(url)
factory = sessionmaker(bind=engine)
session = scoped_session(factory)


class Base:

    @classmethod
    def reset(cls):
        cls.metadata.drop_all(engine)
        cls.metadata.create_all(engine)


Base = declarative_base(cls=Base)
Base.query = session.query_property()


class GeonamesCity(Base):

    __tablename__ = 'geonames_city'

    geonameid = Column(Integer, primary_key=True)

    name = Column(String, nullable=False)

    asciiname = Column(String)

    alternatenames = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    feature_class = Column(String)

    feature_code = Column(String)

    country_code = Column(String, index=True)

    cc2 = Column(String)

    admin1_code = Column(String)

    admin2_code = Column(String)

    admin3_code = Column(String)

    admin4_code = Column(String)

    population = Column(Integer)

    elevation = Column(Integer)

    dem = Column(Integer)

    timezone = Column(String)

    modification_date = Column(String)

    def __repr__(self):
        return f'<City:{self.name},{self.admin1_code}>'

    @property
    def state_abbr(self):
        return self.admin1_code

    @property
    def state_name(self):
        return us.states.lookup(self.admin1_code).name

    def keys_iter(self):
        """Generate variants.
        """
        # State abbreviation / full name.
        states = (self.state_abbr, self.state_name)

        # Comma, no comma between name and state.
        commas = (',', '')

        for state, comma in product(states, commas):
            yield make_key(f'{self.name}{comma} {state}')

        # TODO: Parametrize.
        if self.population > 500000:
            yield make_key(self.name)

        # TODO: Alternate names.


class WOFLocality(Base):

    __tablename__ = 'wof_locality'

    wof_id = Column(Integer, primary_key=True)

    country_iso = Column(String)

    name = Column(String)


@attr.s
class GeonamesCityCSV:

    path = attr.ib()

    def mappings_iter(self):
        """Generate rows dicts.
        """
        cols = GeonamesCity.__table__.columns.keys()

        with open(self.path) as fh:

            reader = csv.DictReader(fh, delimiter='\t', quoting=csv.QUOTE_NONE,
                fieldnames=cols)

            yield from reader

    def load_db(self, n=10000):
        """Insert database rows.
        """
        GeonamesCity.reset()

        for mappings in tqdm(chunked_iter(self.mappings_iter(), n)):
            session.bulk_insert_mappings(GeonamesCity, mappings)
            session.flush()

        session.commit()


@attr.s
class WOFLocalitiesRepo:

    root = attr.ib()

    def paths_iter(self):
        """Glob .geojson paths.
        """
        pattern = os.path.join(self.root, '**/*.geojson')
        return iglob(pattern, recursive=True)

    def locs_iter(self):
        """Generate parsed docs.
        """
        for path in self.paths_iter():
            yield WOFLocalityGeojson.from_json(path)

    def mappings_iter(self):
        """Generate database rows.
        """
        cols = WOFLocality.__table__.columns.keys()

        for loc in self.locs_iter():
            yield {col: getattr(loc, col) for col in cols}

    def load_db(self, n=1000):
        """Insert database rows.
        """
        WOFLocality.reset()

        for mappings in tqdm(chunked_iter(self.mappings_iter(), n)):
            session.bulk_insert_mappings(WOFLocality, mappings)
            session.flush()

        session.commit()


class WOFLocalityGeojson(UserDict):

    @classmethod
    def from_json(cls, path):
        with open(path) as fh:
            return cls(ujson.load(fh))

    def __repr__(self):
        return '%s<%d>' % (self.__class__.__name__, self.id)

    @property
    def wof_id(self):
        return self['id']

    @property
    def country_iso(self):
        return self['properties']['iso:country']

    @property
    def name(self):
        return safe_get(self, 'properties', 'name:eng_x_preferred')


class CityIndex:

    @classmethod
    def from_geonames(cls):
        """Index US Geonames cities.
        """
        idx = defaultdict(list)

        cities = GeonamesCity.query.filter(GeonamesCity.country_code=='US')

        for city in tqdm(cities):
            for key in city.keys_iter():
                idx[key].append(city.geonameid)

        return cls(idx)

    def __init__(self, idx):
        self._idx = idx

    def __getitem__(self, query):
        return self._idx.get(make_key(query))
