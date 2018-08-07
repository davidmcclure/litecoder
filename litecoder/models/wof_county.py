

from sqlalchemy import Column, Integer, String, Float

from .base import BaseModel


class WOFCounty(BaseModel):

    __tablename__ = 'wof_county'

    wof_id = Column(Integer, primary_key=True)

    wof_continent_id = Column(Integer)

    wof_country_id = Column(Integer)

    wof_region_id = Column(Integer)

    fips_code = Column(String)

    hasc_id = Column(String)

    wd_id = Column(String)

    name = Column(String)

    country_iso = Column(String)

    name_a0 = Column(String)

    name_a1 = Column(String)

    latitude = Column(Float)

    longitude = Column(Float)

    population = Column(Integer)

    area_m2 = Column(Float)
