

import pytest

from invoke import task
from subprocess import call

from litecoder.db import engine
from litecoder import logger, US_STATE_PATH, US_CITY_PATH
from litecoder.models import BaseModel, WOFLocality
from litecoder.usa import USStateIndex, USCityIndex

from litecoder.sources.wof import (
    WOFRegionRepo, WOFCountyRepo, WOFLocalityRepo
)


@task
def create_db(c):
    """Create all tables.
    """
    BaseModel.metadata.create_all(engine)


@task
def drop_db(c):
    """Drop all tables.
    """
    BaseModel.metadata.drop_all(engine)


@task(drop_db, create_db)
def reset_db(c):
    """Drop + create tables.
    """
    pass


@task(reset_db)
def load_db(c):
    """Load SQLite tables.
    """
    logger.info('Loading regions.')
    WOFRegionRepo.from_env().load_db()

    logger.info('Loading counties.')
    WOFCountyRepo.from_env().load_db()

    logger.info('Loading localities.')
    WOFLocalityRepo.from_env().load_db()


@task
def clean_db(c):
    """Database post-processing.
    """
    logger.info('Cleaning localities.')
    WOFLocality.dedupe()


@task
def build_indexes(c):
    """Build dist indexes.
    """
    logger.info('Indexing states.')
    state_idx = USStateIndex()
    state_idx.build()
    state_idx.save(US_STATE_PATH)

    logger.info('Indexing cities.')
    city_idx = USCityIndex()
    city_idx.build()
    city_idx.save(US_CITY_PATH)


@task(build_indexes)
def test(c):
    """Run test suite.
    """
    c.run('pytest tests/test_db')
    c.run('pytest tests/prod_db')


@task(load_db, clean_db, build_indexes, test)
def build(c):
    """Load SQLite, build indexes, test.
    """
    pass
