

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.inspection import inspect

from ..db import session


class BaseModel:

    @classmethod
    def column_names(cls):
        """Get a list of column names.
        """
        return cls.__table__.columns.keys()

    def __iter__(self):
        """Generate column / value tuples.

        Yields: (key, val)
        """
        md = inspect(self.__class__)

        for key in md.attrs.keys():
            yield (key, getattr(self, key))

        for key in md.relationships.keys():

            # Try to hydrate FK.
            row = getattr(self, key)

            # If exists, make nested dict.
            if row:
                yield (key, dict(getattr(self, key)))


BaseModel = declarative_base(cls=BaseModel)

BaseModel.query = session.query_property()
