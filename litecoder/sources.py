

import attr
import os
import ujson

from collections import UserDict
from glob import iglob
from multiprocessing import Pool


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

    @property
    def wof_id(self):
        return self['id']

    @property
    def name(self):
        return self['properties']['name:eng_x_preferred'][0]
