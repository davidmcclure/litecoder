

import attr
import os
import ujson
import time

from collections import UserDict
from glob import iglob
from multiprocessing import Pool


class safe_property:

    @classmethod
    def cached(cls, func):
        return cls(func, True)

    def __init__(self, func, cached=False):
        self.cached = cached
        self.__doc__ = getattr(func, "__doc__")
        self.func = func

    def __get__(self, obj, cls):
        """Try to set a cached property. Catch and record errors.
        """
        if obj is None:
            return self

        try:
            value = self.func(obj)
        except Exception as e:
            value = None

        # Replace attribute with computed value.
        if self.cached:
            obj.__dict__[self.func.__name__] = value

        return value


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
        return '%s<%d>' % (self.__class__.__name__, self.wof_id)

    @property
    def wof_id(self):
        return self['id']

    @safe_property
    def name(self):
        return self['properties']['name:eng_x_preferred'][0]
