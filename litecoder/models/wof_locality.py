

import yaml
import pkgutil
import us

import numpy as np

from sqlalchemy import Column, Integer, String, Float, ForeignKey

from ..utils import safe_property
from .base import BaseModel


# TODO: Make pluggable.
CITY_ALT_NAMES = yaml.load(pkgutil.get_data(
    'litecoder', 'data/city-alt-names.yml'
))


class WOFLocality(BaseModel):

    __tablename__ = 'wof_locality'

    wof_id = Column(Integer, primary_key=True)

    wof_region_id = Column(Integer)

    dbp_id = Column(String)

    fb_id = Column(String)

    fct_id = Column(String)

    fips_code = Column(String)

    gn_id = Column(Integer)

    gp_id = Column(Integer)

    loc_id = Column(String)

    nyt_id = Column(String)

    qs_id = Column(Integer)

    qs_pg_id = Column(Integer)

    wd_id = Column(String)

    wk_page = Column(String)

    name = Column(String)

    country_iso = Column(String)

    name_a0 = Column(String)

    name_a1 = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    population = Column(Integer)

    wikipedia_wordcount = Column(Integer)

    elevation = Column(Integer)

    area_m2 = Column(Float)

    @classmethod
    def median_population(cls):
        """Get median population.
        """
        pops = [c.population for c in cls.query if c.population]
        return np.median(pops)

    def __repr__(self):
        return '%s<%s, %s, %s, wof:%d>' % (
            self.__class__.__name__,
            self.name, self.name_a1, self.name_a0, self.wof_id,
        )

    @property
    def completeness(self):
        """Count non-null fields.
        """
        return len([k for k, v in dict(self).items() if v is not None])

    # TODO: Make name list pluggable.
    @property
    def alt_names(self):
        """Map alt names via Wikidata id.
        """
        return CITY_ALT_NAMES.get(self.wikidata_id, [])

    @property
    def names(self):
        """Name + alt names.
        """
        return set((self.name, *self.alt_names))

    # TODO: Get from region?
    @safe_property
    def us_state_abbr(self):
        """A1 name -> US state abbreviation.
        """
        return us.states.lookup(self.name_a1).abbr
