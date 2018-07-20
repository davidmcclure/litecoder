

import us
import pkgutil
import yaml

import numpy as np

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import deferred
from sqlalchemy import Column, Integer, String, Float, Text

from .db import session, engine
from .utils import safe_property


# TODO: Seprate module?
CITY_ALT_NAMES = yaml.load(pkgutil.get_data(
    'litecoder', 'data/city-alt-names.yml'
))


class BaseModel:

    @classmethod
    def reset(cls):
        """Drop and (re-)create table.
        """
        cls.metadata.drop_all(engine)
        cls.metadata.create_all(engine)

    @classmethod
    def column_names(cls):
        """Get a list of column names.
        """
        return cls.__table__.columns.keys()

    def __iter__(self):
        """Generate column / value tuples.

        Yields: (key, val)
        """
        for key in self.column_names():
            if key in self.__dict__:
                yield (key, getattr(self, key))


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

    wikipedia_wordcount = Column(Integer)

    elevation = Column(Integer)

    area_m2 = Column(Float)

    # geometry_json = deferred(Column(Text))

    @classmethod
    def median_population(cls):
        """Get median population.
        """
        pops = [c.population for c in cls.query if c.population]
        return np.median(pops)

    def __repr__(self):
        return '%s<%d, %s, %s, %s>' % (
            self.__class__.__name__,
            self.wof_id,
            self.name,
            self.name_a1,
            self.name_a0,
        )

    @property
    def alt_names(self):
        return CITY_ALT_NAMES.get(self.wikidata_id, [])

    @property
    def names(self):
        return set((self.name, *self.alt_names))

    @safe_property
    def us_state_abbr(self):
        return us.states.lookup(self.name_a1).abbr
