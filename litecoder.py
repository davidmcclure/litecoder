

import attr
import os
import csv
import us
import re

from boltons.iterutils import chunked_iter
from tqdm import tqdm
from collections import defaultdict
from itertools import product

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float


def make_key(text, lower=True):
    """Normalize text string -> index key.
    """
    text = text.strip()
    text = re.sub('\s{2,}', ' ', text)

    if lower:
        text = text.lower()

    return text


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


@attr.s
class GeonamesCityCSV:

    path = attr.ib()

    def rows_iter(self):
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

        for chunk in tqdm(chunked_iter(self.rows_iter(), n)):
            session.bulk_insert_mappings(GeonamesCity, chunk)
            session.flush()

        session.commit()


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
