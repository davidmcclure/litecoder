

from sqlalchemy.ext.declarative import declarative_base

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
        for key in self.column_names():
            if key in self.__dict__:
                yield (key, getattr(self, key))


BaseModel = declarative_base(cls=BaseModel)

BaseModel.query = session.query_property()
