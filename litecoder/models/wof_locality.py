

import yaml
import pkgutil
import us

import numpy as np

from tqdm import tqdm
from collections import defaultdict
from scipy.spatial import cKDTree

from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

from ..db import session
from ..utils import safe_property
from .. import logger
from .base import BaseModel


# TODO: Make pluggable.
CITY_ALT_NAMES = yaml.load(pkgutil.get_data(
    'litecoder', 'data/city-alt-names.yml'
))


ID_COLS = (
    'dbp_id',
    'fb_id',
    'fct_id',
    'fips_code',
    'gn_id',
    'gp_id',
    'loc_id',
    'nyt_id',
    'qs_id',
    'qs_pg_id',
    'wd_id',
    'wk_page',
)


class WOFLocality(BaseModel):

    __tablename__ = 'wof_locality'

    wof_id = Column(Integer, primary_key=True)

    wof_continent_id = Column(Integer)

    wof_country_id = Column(Integer)

    wof_region_id = Column(Integer)

    wof_county_id = Column(Integer)

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

    duplicate = Column(Boolean, default=False)

    # TODO: Handle NYC, with separate county for each borough.
    county = relationship(
        'WOFCounty',
        primaryjoin='WOFCounty.wof_id==WOFLocality.wof_county_id',
        foreign_keys=[wof_county_id],
    )

    region = relationship(
        'WOFRegion',
        primaryjoin='WOFRegion.wof_id==WOFLocality.wof_region_id',
        foreign_keys=[wof_region_id],
    )

    @classmethod
    def set_dupes(cls, wof_ids):
        """Apply duplicate list.

        Args:
            wof_ids (iter)
        """
        dupes = cls.query.filter(cls.wof_id.in_(wof_ids))
        dupes.update({cls.duplicate: True}, synchronize_session=False)
        session.commit()

    @classmethod
    def dedupe_id_col(cls, name):
        """Dedupe localities via identifier column.
        """
        dup_col = getattr(cls, name)

        logger.info('Mapping `%s` -> rows' % name)

        id_rows = defaultdict(list)
        for row in tqdm(cls.query.filter(dup_col != None)):
            id_rows[getattr(row, name)].append(row)

        logger.info('Deduping rows with shared `%s`' % name)

        dupes = set()
        for rows in tqdm(id_rows.values()):
            if len(rows) > 1:

                # Sort by completeness.
                rows = sorted(rows, key=lambda r: r.field_count, reverse=True)

                # Add all but most complete to dupes.
                for row in rows[1:]:
                    dupes.add(row.wof_id)

        cls.set_dupes(dupes)

    @classmethod
    def dedupe_proximity(cls, buffer=0.1):
        """Find duplicates within N degrees.
        """
        # Pre-load rows.
        rows = cls.query.all()
        id_row = {i: row for i, row in enumerate(rows)}

        # Build index.
        data = [[r.longitude, r.latitude] for r in rows]
        idx = cKDTree(data)

        logger.info('Deduping rows within %.2f°' % buffer)

        dupes = set()
        for id1, id2 in tqdm(idx.query_pairs(buffer)):

            row1, row2 = id_row[id1], id_row[id2]

            if row1.name == row2.name:

                dupes.add(row1.wof_id if row1.field_count < row2.field_count
                    else row2.wof_id)

        cls.set_dupes(dupes)

    @classmethod
    def dedupe(cls, *args, **kwargs):
        """Dedupe by shared ids + proximity.
        """
        for name in ID_COLS:
            cls.dedupe_id_col(name)

        cls.dedupe_proximity(*args, **kwargs)

    @classmethod
    def clean_query(cls):
        """Build deduped query.
        """
        return cls.query.filter(cls.duplicate==False)

    @classmethod
    def clean_us_cities(cls):
        """Select clean US cities with city + state names.
        """
        return (cls.clean_query()
            .filter(cls.country_iso=='US')
            .filter(cls.name != None)
            .filter(cls.name_a1 != None))

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
    def field_count(self):
        """Count non-null fields.
        """
        return len([k for k, v in dict(self).items() if v is not None])

    # TODO: Make name list pluggable.
    @property
    def alt_names(self):
        """Map alt names via Wikidata id.
        """
        return CITY_ALT_NAMES.get(self.wd_id, [])

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
