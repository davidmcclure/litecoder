

import os
import csv
import sys
import us

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

    @classmethod
    def lookup(cls, key, country_code=None):
        """Find cities by index key.
        """
        query = (
            session.query(cls)
            .join(CityIndex)
            .filter(CityIndex.name==collate(key, 'nocase'))
        )

        if country_code:
            query = query.filter(cls.country_code==country_code)

        return query.all()


class CityIndex(Base):

    __tablename__ = 'city_index'

    id = Column(Integer, primary_key=True)

    geonameid = Column(Integer, ForeignKey('city.geonameid'))

    key = Column(String, nullable=False)

    @classmethod
    def load(cls):
        """Load from CSV.
        """
        for city in tqdm(City.query.yield_per(1000)):

            tokens = TokenList.from_text(city.name)

            row = cls(geonameid=city.geonameid, key=tokens.key())
            session.add(row)

        session.commit()


Index('city_index_key', collate(CityIndex.key, 'nocase'))


class StateIndex(dict):

    def __init__(self):
        """Index name -> state.
        """
        for state in us.STATES:
            self[state.abbr.lower()] = state
            self[state.name.lower()] = state


state_index = StateIndex()
