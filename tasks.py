

from invoke import task

from litecoder.db import Base, engine, City, CityIndex


@task
def drop_db(ctx):
    Base.metadata.drop_all(engine)


@task
def create_db(ctx):
    Base.metadata.create_all(engine)


@task(drop_db, create_db)
def reset_db(ctx):
    pass


@task
def load_db(ctx, path):
    City.load(path)
    CityIndex.load()
