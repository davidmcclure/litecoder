

import os
import us

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Text

from .utils import safe_property


# TODO: Config-ify
db_path = os.path.join(
    os.path.dirname(__file__),
    'data', 'litecoder.db',
)

url = URL(drivername='sqlite', database=db_path)
engine = create_engine(url)
factory = sessionmaker(bind=engine)
session = scoped_session(factory)


class BaseModel:

    @classmethod
    def reset(cls):
        """Drop and (re-)create table.
        """
        cls.metadata.drop_all(engine)
        cls.metadata.create_all(engine)


BaseModel = declarative_base(cls=BaseModel)
BaseModel.query = session.query_property()


class City(BaseModel):

    __tablename__ = 'city'

    wof_id = Column(Integer, primary_key=True)

    dbpedia_id = Column(String)

    freebase_id = Column(String)

    factual_id = Column(String)

    fips_code = Column(Integer)

    geonames_id = Column(Integer)

    geoplanet_id = Column(Integer)

    library_of_congress_id = Column(String)

    new_york_times_id = Column(String)

    quattroshapes_id = Column(Integer)

    wikidata_id = Column(String)

    wikipedia_page = Column(String)

    name = Column(String, nullable=False)

    country_iso = Column(String, nullable=False)

    name_a0 = Column(String)

    name_a1 = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    population = Column(Integer)

    population_rank = Column(Integer)

    wikipedia_wordcount = Column(Integer)

    elevation = Column(Integer)

    area_m2 = Column(Float)

    geometry_json = Column(Text)

    @safe_property
    def us_state_abbr(self):
        return us.states.lookup(self.name_a1).abbr
