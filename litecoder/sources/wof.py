

import attr
import os
import ujson
import time
import us

from collections import UserDict
from glob import iglob
from boltons.iterutils import chunked_iter
from multiprocessing import Pool
from tqdm import tqdm
from itertools import islice

from .. import logger, DATA_DIR
from ..utils import safe_property, first, read_json
from ..db import session
from ..models import WOFLocality, WOFRegion, WOFCounty


@attr.s
class WOFRepo:

    root = attr.ib()

    def paths_iter(self):
        """Glob paths.
        """
        pattern = os.path.join(self.root, '**/*.geojson')
        return iglob(pattern, recursive=True)

    def docs_iter(self, num_procs=None):
        """Generate parsed GeoJSON docs.
        """
        with Pool(num_procs) as p:
            yield from p.imap_unordered(read_json, self.paths_iter())

    def db_rows_iter(self):
        raise NotImplementedError

    def load_db(self, n=1000):
        """Load database rows.
        """
        rows = tqdm(self.db_rows_iter())

        for rows in chunked_iter(iter(rows), n):
            session.bulk_save_objects(rows)
            session.commit()


class WOFRegionRepo(WOFRepo):

    @classmethod
    def from_env(cls):
        return cls(os.path.join(DATA_DIR, 'wof-region'))

    def db_rows_iter(self):
        for doc in self.docs_iter():
            yield WOFRegionDoc(doc).db_row()


class WOFCountyRepo(WOFRepo):

    @classmethod
    def from_env(cls):
        return cls(os.path.join(DATA_DIR, 'wof-county'))

    def db_rows_iter(self):
        for doc in self.docs_iter():
            yield WOFCountyDoc(doc).db_row()


class WOFLocalityRepo(WOFRepo):

    @classmethod
    def from_env(cls):
        return cls(os.path.join(DATA_DIR, 'wof-locality'))

    def db_rows_iter(self):
        for doc in self.docs_iter():
            yield WOFLocalityDoc(doc).db_row()


class WOFDoc(UserDict):

    @classmethod
    def from_path(cls, path):
        return cls(read_json(path))

    def __repr__(self):
        return '%s<%d>' % (self.__class__.__name__, self.wof_id)

    @safe_property
    def wof_id(self):
        return self['id']

    def _wof_hierarchy_id(self, key):
        """Get WOF hierarchy id, if unique.
        """
        ids = set([
            h['%s_id' % key]
            for h in self['properties']['wof:hierarchy']
        ])

        # TODO: Handle 2+ links.
        # Punt when more than one link.
        if len(ids) == 1:
            id = list(ids)[0]
            return id if id > 0 else None

    @safe_property
    def wof_continent_id(self):
        return self._wof_hierarchy_id('continent')

    @safe_property
    def wof_country_id(self):
        return self._wof_hierarchy_id('country')

    @safe_property
    def wof_region_id(self):
        return self._wof_hierarchy_id('region')

    @safe_property
    def wof_county_id(self):
        return self._wof_hierarchy_id('county')

    @safe_property
    def dbp_id(self):
        return self['properties']['wof:concordances']['dbp:id']

    @safe_property
    def fb_id(self):
        return self['properties']['wof:concordances']['fb:id']

    @safe_property
    def fct_id(self):
        return self['properties']['wof:concordances']['fct:id']

    @safe_property
    def fips_code(self):
        return self['properties']['wof:concordances']['fips:code']

    @safe_property
    def gn_id(self):
        return self['properties']['wof:concordances']['gn:id']

    @safe_property
    def gp_id(self):
        return self['properties']['wof:concordances']['gp:id']

    @safe_property
    def hasc_id(self):
        return self['properties']['wof:concordances']['hasc:id']

    @safe_property
    def iso_id(self):
        return self['properties']['wof:concordances']['iso:id']

    @safe_property
    def unlc_id(self):
        return self['properties']['wof:concordances']['unlc:id']

    @safe_property
    def loc_id(self):
        return self['properties']['wof:concordances']['loc:id']

    @safe_property
    def nyt_id(self):
        return self['properties']['wof:concordances']['nyt:id']

    @safe_property
    def qs_id(self):
        return self['properties']['wof:concordances']['qs:id']

    @safe_property
    def qs_pg_id(self):
        return self['properties']['wof:concordances']['qs_pg:id']

    @safe_property
    def wd_id(self):
        return self['properties']['wof:concordances']['wd:id']

    @safe_property
    def wk_page(self):
        return self['properties']['wof:concordances']['wk:page']

    @safe_property
    def country_iso(self):
        return self['properties']['iso:country']

    @safe_property
    def _gn_latitude(self):
        return self['properties']['gn:latitude']

    @safe_property
    def _geom_latitude(self):
        return self['properties']['geom:latitude']

    @safe_property
    def latitude(self):
        return first(
            self._gn_latitude,
            self._geom_latitude,
        )

    @safe_property
    def _gn_longitude(self):
        return self['properties']['gn:longitude']

    @safe_property
    def _geom_longitude(self):
        return self['properties']['geom:longitude']

    @safe_property
    def longitude(self):
        return first(
            self._gn_longitude,
            self._geom_longitude,
        )

    @safe_property
    def _gn_population(self):
        return self['properties']['gn:population']

    @safe_property
    def _wof_population(self):
        return self['properties']['wof:population']

    @safe_property
    def _wk_population(self):
        return self['properties']['wk:population']

    @safe_property
    def population(self):
        return first(
            self._gn_population,
            self._wof_population,
            self._wk_population,
        )

    @safe_property
    def area_m2(self):
        return self['properties']['geom:area_square_m']

    @safe_property
    def _name_eng_x_preferred(self):
        return self['properties']['name:eng_x_preferred'][0]

    @safe_property
    def _wof_name(self):
        return self['properties']['wof:name']

    @safe_property
    def _qs_pg_name(self):
        return self['properties']['qs_pg:name']

    @safe_property
    def name(self):
        return first(
            self._name_eng_x_preferred,
            self._wof_name,
            self._qs_pg_name,
        )

    @safe_property
    def _qs_a0(self):
        return self['properties']['qs:a0']

    @safe_property
    def _qs_adm0(self):
        return self['properties']['qs:adm0']

    @safe_property
    def _ne_sov0name(self):
        return self['properties']['ne:SOV0NAME']

    @safe_property
    def _qs_pg_name_adm0(self):
        return self['properties']['qs_pg:name_adm0']

    @safe_property
    def _woe_name_adm0(self):
        return self['properties']['woe:name_adm0']

    @safe_property
    def name_a0(self):
        return first(
            self._qs_a0,
            self._qs_adm0,
            self._ne_sov0name,
            self._qs_pg_name_adm0,
            self._woe_name_adm0,
        )

    @safe_property
    def _qs_a1(self):
        return self['properties']['qs:a1'].strip('*')

    @safe_property
    def _ne_adm1name(self):
        return self['properties']['ne:ADM1NAME']

    @safe_property
    def _qs_pg_name_adm1(self):
        return self['properties']['qs_pg:name_adm1']

    @safe_property
    def _woe_name_adm1(self):
        return self['properties']['woe:name_adm1']

    @safe_property
    def name_a1(self):
        return first(
            self._qs_a1,
            self._ne_adm1name,
            self._qs_pg_name_adm1,
            self._woe_name_adm1,
        )


class WOFRegionDoc(WOFDoc):

    @safe_property
    def _abrv_eng_x_preferred(self):
        return self['properties']['abrv:eng_x_preferred'][0]

    @safe_property
    def _wof_abbreviation(self):
        return self['properties']['wof:abbreviation']

    @safe_property
    def name_abbr(self):
        return first(
            self._abrv_eng_x_preferred,
            self._wof_abbreviation,
        )

    def db_row(self):
        """Returns: models.WOFRegion
        """
        return WOFRegion(**{
            col: getattr(self, col)
            for col in WOFRegion.column_names()
            if hasattr(self, col)
        })


class WOFCountyDoc(WOFDoc):

    def db_row(self):
        """Returns: models.WOFCounty
        """
        return WOFCounty(**{
            col: getattr(self, col)
            for col in WOFCounty.column_names()
            if hasattr(self, col)
        })


class WOFLocalityDoc(WOFDoc):

    @safe_property
    def wikipedia_wordcount(self):
        return self['properties']['wk:wordcount']

    @safe_property
    def _gn_elevation(self):
        return self['properties']['gn:elevation']

    @safe_property
    def _ne_elevation(self):
        return self['properties']['ne:ELEVATION']

    @safe_property
    def elevation(self):
        return first(
            self._gn_elevation,
            self._ne_elevation,
        )

    def db_row(self):
        """Returns: models.WOFLocality
        """
        return WOFLocality(**{
            col: getattr(self, col)
            for col in WOFLocality.column_names()
            if hasattr(self, col)
        })
