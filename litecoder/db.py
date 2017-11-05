

import os
import csv
import sys

from boltons.iterutils import chunked_iter
from tqdm import tqdm

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
)

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.ext.declarative import declarative_base

from .parsers import ToponymTokens


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

    country_code = Column(String)

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
                session.commit()


class CityIndex(Base):

    __tablename__ = 'city_index'

    geonameid = Column(
        Integer,
        ForeignKey('city.geonameid'),
        primary_key=True,
    )

    city = relationship('City')

    key = Column(String, nullable=False)

    @classmethod
    def load(cls):
        """Index keys.
        """
        query = session.query(City.geonameid, City.name)

        for id, name in tqdm(query):
            tokens = ToponymTokens.from_text(name)
            session.add(cls(geonameid=id, key=tokens.key))

        session.commit()
