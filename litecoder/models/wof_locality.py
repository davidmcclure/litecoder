

import yaml
import pkgutil
import us

import numpy as np

from sqlalchemy import Column, Integer, String, Float, ForeignKey, func

from tqdm import tqdm
from shapely.strtree import STRtree
from shapely.geometry import Point

from .. import logger
from ..utils import safe_property
from ..db import session
from .base import BaseModel


# TODO: Make pluggable.
CITY_ALT_NAMES = yaml.load(pkgutil.get_data(
    'litecoder', 'data/city-alt-names.yml'
))


class WOFLocality(BaseModel):

    __tablename__ = 'wof_locality'

    wof_id = Column(Integer, primary_key=True)

    wof_continent_id = Column(Integer)

    wof_country_id = Column(Integer)

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


class WOFLocalityDup(BaseModel):

    __tablename__ = 'locality_dup'

    wof_id = Column(Integer, ForeignKey(WOFLocality.wof_id), primary_key=True)

    @classmethod
    def update(cls, wof_ids):
        """Merge in new dupes.

        Args:
            wof_ids (set)
        """
        existing = set([r.wof_id for r in cls.query])
        new = wof_ids - existing

        session.bulk_save_objects([cls(wof_id=wof_id) for wof_id in new])
        session.commit()

    @classmethod
    def dedupe_by_proximity(cls, buffer=0.1):
        """For each locality, get neighbors within N degrees. If any of these
        (a) has the same name and (b) has more complete metadata, set dupe.
        """
        # Cache rows for speed.
        rows = WOFLocality.query.filter(WOFLocality.country_iso=='US').all()
        id_row = {row.wof_id: row for row in rows}

        logger.info('Building rtree on %d localities' % len(rows))

        # Build rtree index.
        points = []
        for row in tqdm(rows):
            p = Point(row.longitude, row.latitude)
            p.wof_id = row.wof_id
            points.append(p)

        idx = STRtree(points)

        logger.info('Querying for duplicates')

        dupes = set()
        for row, point in zip(tqdm(rows), points):

            # Find localities within a given radius.
            close = idx.query(point.buffer(buffer))
            close_ids = [p.wof_id for p in close if p.wof_id != row.wof_id]
            nn = [id_row[id] for id in close_ids]

            # If same name and more complete, register this row as a dupe.
            for other in nn:
                if (other.name == row.name and
                    other.completeness > row.completeness):
                    dupes.add(row.wof_id)
                    break

        cls.update(dupes)

    @classmethod
    def dedupe_shared_id_col(cls, col_name):
        """Dedupe localities via shared external identifier.
        """
        dup_col = getattr(WOFLocality, col_name)

        # Select ids with 2+ records.
        query = (session
            .query(dup_col)
            .filter(dup_col != None)
            .group_by(dup_col)
            .having(func.count(WOFLocality.wof_id) > 1)
            .all())

        dupes = set()
        for r in tqdm(query):

            # Load rows, sort by completeness.
            rows = WOFLocality.query.filter(dup_col==r[0])
            rows = sorted(rows, key=lambda r: r.completeness, reverse=True)

            # Add all but most complete to dupes.
            for row in rows[1:]:
                dupes.add(row.wof_id)

        cls.update(dupes)
