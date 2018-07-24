

from sqlalchemy import Column, Integer, String, Float

from .base import BaseModel


class Region(BaseModel):

    __tablename__ = 'region'

    wof_id = Column(Integer, primary_key=True)

    wof_country_id = Column(Integer)

    fips_code = Column(String)

    geonames_id = Column(Integer)

    geoplanet_id = Column(Integer)

    iso_id = Column(String)

    wikidata_id = Column(String)

    name = Column(String)

    name_abbr = Column(String)

    country_iso = Column(String)

    name_a0 = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    population = Column(Integer)

    area_m2 = Column(Float)

    def __repr__(self):
        return '%s<%s, %s, wof:%d>' % (
            self.__class__.__name__,
            self.name, self.name_a0, self.wof_id,
        )
