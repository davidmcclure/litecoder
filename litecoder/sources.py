

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

from . import logger
from .utils import safe_property, first, read_json
from .db import session
from .models import City


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


class WOFLocalitiesRepo(WOFRepo):

    def locs_iter(self, *args, **kwargs):
        """Generate parsed locality instances.
        """
        for data in self.docs_iter(*args, **kwargs):
            yield WOFLocalityGeojson(data)

    def load_db(self):
        """Load US cities database.
        """
        City.reset()

        for loc in tqdm(self.locs_iter()):

            try:
                session.add(loc.db_row())
                session.commit()

            except Exception as e:
                session.rollback()
                print(e)


class WOFLocalityGeojson(UserDict):

    @classmethod
    def from_path(cls, path):
        return cls(read_json(path))

    def __repr__(self):
        return '%s<%d>' % (self.__class__.__name__, self.wof_id)

    @safe_property
    def wof_id(self):
        return self['id']

    @safe_property
    def wof_parent_id(self):
        return self['properties']['wof:parent_id']

    @safe_property
    def dbpedia_id(self):
        return self['properties']['wof:concordances']['dbp:id']

    @safe_property
    def freebase_id(self):
        return self['properties']['wof:concordances']['fb:id']

    @safe_property
    def factual_id(self):
        return self['properties']['wof:concordances']['fct:id']

    @safe_property
    def fips_code(self):
        return self['properties']['wof:concordances']['fips:code']

    @safe_property
    def geonames_id(self):
        return self['properties']['wof:concordances']['gn:id']

    @safe_property
    def geoplanet_id(self):
        return self['properties']['wof:concordances']['gp:id']

    @safe_property
    def library_of_congress_id(self):
        return self['properties']['wof:concordances']['loc:id']

    @safe_property
    def new_york_times_id(self):
        return self['properties']['wof:concordances']['nyt:id']

    @safe_property
    def quattroshapes_id(self):
        return self['properties']['wof:concordances']['qs:id']

    @safe_property
    def wikidata_id(self):
        return self['properties']['wof:concordances']['wd:id']

    @safe_property
    def wikipedia_page(self):
        return self['properties']['wof:concordances']['wk:page']

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
        return first((
            self._name_eng_x_preferred,
            self._wof_name,
            self._qs_pg_name,
        ))

    @safe_property
    def country_iso(self):
        return self['properties']['iso:country']

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
        return first((
            self._qs_a0,
            self._qs_adm0,
            self._ne_sov0name,
            self._qs_pg_name_adm0,
            self._woe_name_adm0,
        ))

    @safe_property
    def _qs_a1(self):
        return self['properties']['qs:a1'][1:]

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
        return first((
            self._qs_a1,
            self._ne_adm1name,
            self._qs_pg_name_adm1,
            self._woe_name_adm1,
        ))

    @safe_property
    def latitude(self):
        return self['properties']['geom:latitude']

    @safe_property
    def longitude(self):
        return self['properties']['geom:latitude']

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
        return first((
            self._gn_population,
            self._wof_population,
            self._wk_population,
        ))

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
        return first((self._gn_elevation, self._ne_elevation))

    @safe_property
    def area_m2(self):
        return self['properties']['geom:area_square_m']

    def db_row(self):
        """Build city database row instance.
        """
        return City(**{
            col: getattr(self, col)
            for col in City.column_names()
        })


class WOFRegionGeojson(UserDict):

    @classmethod
    def from_path(cls, path):
        return cls(read_json(path))

    def __repr__(self):
        return '%s<%d>' % (self.__class__.__name__, self.wof_id)

    @safe_property
    def wof_id(self):
        return self['id']

    @safe_property
    def wof_parent_id(self):
        return self['properties']['wof:parent_id']

    @safe_property
    def fips_code(self):
        return self['properties']['wof:concordances']['fips:code']

    @safe_property
    def geonames_id(self):
        return self['properties']['wof:concordances']['gn:id']

    @safe_property
    def geoplanet_id(self):
        return self['properties']['wof:concordances']['gp:id']

    @safe_property
    def iso_id(self):
        return self['properties']['wof:concordances']['iso:id']

    @safe_property
    def wikidata_id(self):
        return self['properties']['wof:concordances']['wd:id']

    @safe_property
    def _name_eng_x_preferred(self):
        return self['properties']['name:eng_x_preferred'][0]

    @safe_property
    def _wof_name(self):
        return self['properties']['wof:name']

    @safe_property
    def name(self):
        return first((
            self._name_eng_x_preferred,
            self._wof_name,
        ))

    @safe_property
    def name_abbr(self):
        return self['properties']['wof:abbreviation']

    @safe_property
    def country_iso(self):
        return self['properties']['iso:country']

    @safe_property
    def _qs_a0(self):
        return self['properties']['qs:a0']

    @safe_property
    def _qs_adm0(self):
        return self['properties']['qs:adm0']

    @safe_property
    def name_a0(self):
        return first((
            self._qs_a0,
            self._qs_adm0,
        ))

    @safe_property
    def latitude(self):
        return self['properties']['geom:latitude']

    @safe_property
    def longitude(self):
        return self['properties']['geom:latitude']

    @safe_property
    def _wof_population(self):
        return self['properties']['wof:population']

    @safe_property
    def _statoids_population(self):
        return self['properties']['statoids:population']

    @safe_property
    def population(self):
        return first((
            self._wof_population,
            self._statoids_population,
        ))

    @safe_property
    def area_m2(self):
        return self['properties']['geom:area_square_m']
