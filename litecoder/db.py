

import os

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from . import DATA_DIR


def connect_db(db_path):
    """Get database connection.

    Args:
        db_path (str)

    Returns: engine, session
    """
    url = URL(drivername='sqlite', database=db_path)
    engine = create_engine(url)
    factory = sessionmaker(bind=engine)
    session = scoped_session(factory)
    return engine, session


db_name = 'litecoder.%s.db' % os.environ.get('LITECODER_ENV', 'prod')
db_path = os.path.join(DATA_DIR, db_name)


engine, session = connect_db(db_path)
