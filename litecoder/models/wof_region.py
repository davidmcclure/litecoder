

from sqlalchemy import Column, Integer, String, Float

from .base import BaseModel


class WOFRegion(BaseModel):

    __tablename__ = 'wof_region'

    wof_id = Column(Integer, primary_key=True)

    wof_continent_id = Column(Integer)

    wof_country_id = Column(Integer)

    fips_code = Column(String)

    gn_id = Column(Integer)

    gp_id = Column(Integer)

    hasc_id = Column(String)

    iso_id = Column(String)

    unlc_id = Column(String)

    wd_id = Column(String)

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
