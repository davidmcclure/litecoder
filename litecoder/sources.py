

import attr
import os
import ujson
import time
import us

from collections import UserDict
from glob import iglob
from multiprocessing import Pool

from .utils import safe_property, first
from .db import City


@attr.s
class WOFLocalitiesRepo:

    root = attr.ib()

    def paths_iter(self):
        """Glob .geojson paths.
        """
        pattern = os.path.join(self.root, '**/*.geojson')
        return iglob(pattern, recursive=True)

    def locs_iter(self, num_procs=None):
        """Generate parsed locality documents.
        """
        with Pool(num_procs) as p:

            yield from p.imap_unordered(
                WOFLocalityGeojson,
                self.paths_iter(),
            )


class WOFLocalityGeojson(UserDict):

    def __init__(self, path):
        """Parse JSON, set path.
        """
        with open(path) as fh:
            super().__init__(ujson.load(fh))

        self.path = path

    def __repr__(self):
        return '%s<%d>' % (self.__class__.__name__, self.id_wof)

    @property
    def wof_id(self):
        return self['id']

    @safe_property
    def dbpedia_id(self):
        return self['properties']['wof:concordances']['dbp:id']

    @safe_property
    def freebase_id(self):
        return self['properties']['wof:concordances']['fb:id']

    @safe_property
    def factual_id(self):
        return self['properties']['wof:concordances']['fc:id']

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
    def name(self):
        return self['properties']['name:eng_x_preferred'][0]

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
    def country_name(self):
        return first((self._qs_a0, self._qs_adm0, self._ne_sov0name))

    @safe_property
    def _qs_a1(self):
        return self['properties']['qs:a1'][1:]

    @safe_property
    def _ne_adm1name(self):
        return self['properties']['ne:ADM1NAME']

    @safe_property
    def state_name(self):
        return first((self._qs_a1, self._ne_adm1name))

    @safe_property
    def state_abbr(self):
        return us.states.lookup(self.state_name).abbr

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
    def population_rank(self):
        return self['properties']['wof:population_rank']

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

    @safe_property
    def geometry(self):
        return self['geometry']

    @safe_property
    def geometry_json(self):
        return ujson.dumps(self.geometry)

    @safe_property
    def _name_eng_x_colloquial(self):
        return self['properties']['name:eng_x_colloquial']

    @safe_property
    def _name_eng_x_variant(self):
        return self['properties']['name:eng_x_variant']

    @safe_property
    def alt_names(self):
        namesets = (
            self._name_eng_x_colloquial,
            self._name_eng_x_variant,
        )

        return set([n for ns in namesets if ns for n in ns])

    def is_us_city(self):
        return self.country_iso == 'US' and self.state_abbr

    def db_row(self):
        """Build city database row instance.
        """
        city = City(**{
            col: getattr(self, col)
            for col in City.__table__.columns.keys()
        })

        # TODO: Alt names.

        return city
