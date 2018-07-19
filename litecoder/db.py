

import os

from sqlalchemy.engine.url import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# TODO: Config-ify
db_path = os.path.join(
    os.path.dirname(__file__),
    'data', 'litecoder.db',
)

url = URL(drivername='sqlite', database=db_path)

engine = create_engine(url)

factory = sessionmaker(bind=engine)

session = scoped_session(factory)
