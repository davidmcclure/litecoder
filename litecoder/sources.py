

import attr
import os
import ujson

from collections import UserDict
from glob import iglob
from multiprocessing import Pool


def try_or_log(f):
    """Wrap a class method call in a try block. If an error is raised, return
    None and log the exception.
    """
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # TODO|dev
            # logging.exception('message')
            return None
    return wrapper


class safe_property:

    def __init__(self, func):
        self.__doc__ = getattr(func, "__doc__")
        self.func = func
        self.successes = set()
        self.fails = set()

    def __get__(self, obj, cls):
        """Try to set a cached property. Catch and record errors.
        """
        if obj is None:
            return self

        try:
            value = self.func(obj)
            self.calls.add(obj.wof_id)
        except Exception as e:
            value = None
            self.fails.add(obj.wof_id)

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
                WOFLocalityGeojson.from_json,
                self.paths_iter()
            )


class WOFLocalityGeojson(UserDict):

    @classmethod
    def from_json(cls, path):
        with open(path) as fh:
            return cls(ujson.load(fh))

    def __repr__(self):
        return '%s<%d>' % (self.__class__.__name__, self.id)

    @safe_cached_property
    def wof_id(self):
        return self['id']

    @safe_cached_property
    def name(self):
        return self['properties']['name:eng_x_preferred'][0]
