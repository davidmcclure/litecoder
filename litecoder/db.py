

import os

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, event

from . import LITECODER_ENV, DATA_DIR


def connect_db(db_path):
    """Get database connection.

    Args:
        db_path (str)

    Returns: engine, session
    """
    url = URL(drivername='sqlite', database=db_path)
    engine = create_engine(url)

    # Fix transaction bugs in pysqlite.
    # http://docs.sqlalchemy.org/en/latest/dialects/sqlite.html#pysqlite-serializable

    @event.listens_for(engine, 'connect')
    def on_connect(conn, record):
        conn.execute('pragma foreign_keys=ON')
        conn.isolation_level = None

    @event.listens_for(engine, 'begin')
    def on_begin(conn):
        conn.execute('BEGIN')

    factory = sessionmaker(bind=engine)
    session = scoped_session(factory)

    return engine, session


db_path = os.path.join(DATA_DIR, 'litecoder.db')

# In-memory for tests.
if LITECODER_ENV == 'test':
    db_path = None

engine, session = connect_db(db_path)
