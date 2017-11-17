

import os
import csv
import sys
import us

from collections import defaultdict
from boltons.iterutils import chunked_iter
from tqdm import tqdm

from sqlalchemy import Column, Integer, String, Float, Index, ForeignKey, \
    create_engine, collate

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base

from .parsers import TokenList


db_path = os.path.join(os.path.dirname(__file__), 'litecoder.db')
url = URL(drivername='sqlite', database=db_path)
engine = create_engine(url)
factory = sessionmaker(bind=engine)
session = scoped_session(factory)


Base = declarative_base()
Base.query = session.query_property()


csv.field_size_limit(sys.maxsize)


class City(Base):

    __tablename__ = 'city'

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

    @classmethod
    def load(cls, path, n=1000):
        """Load from CSV.
        """
        cols = cls.__table__.columns.keys()

        with open(path) as fh:

            rows = csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE)

            for chunk in tqdm(chunked_iter(rows, n)):

                mappings = [dict(zip(cols, vals)) for vals in chunk]

                session.bulk_insert_mappings(cls, mappings)
                session.flush()

        session.commit()

    def key(self):
        """Make index key.
        """
        tokens = TokenList.from_text(self.name)
        return tokens.key()


class StateIndex(dict):

    def __init__(self):
        """Index name -> state.
        """
        for state in us.STATES:

            self[state.abbr] = state
            self[state.name] = state

            self[state.abbr.lower()] = state
            self[state.name.lower()] = state


state_index = StateIndex()


class CityIndex:

    def __init__(self):
        """Index key -> city.
        """
        self._index = defaultdict(list)

        query = City.query.filter_by(country_code='US')

        for city in query:
            self._index[city.key()].append(city)

    def __getitem__(self, key):
        return self._index[key]


city_index = CityIndex()
