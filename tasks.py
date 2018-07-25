

from invoke import task

from litecoder import logger, US_STATE_PATH, US_CITY_PATH
from litecoder.sources.wof import WOFRegionRepo, WOFLocalityRepo
from litecoder.db import engine
from litecoder.models import BaseModel
from litecoder.usa import USStateIndex, USCityIndex


@task
def create_db(ctx):
    BaseModel.metadata.create_all(engine)


@task
def drop_db(ctx):
    BaseModel.metadata.drop_all(engine)


@task(drop_db, create_db)
def reset_db(ctx):
    pass


@task(reset_db)
def load_db(ctx):

    logger.info('Loading regions.')
    WOFRegionRepo.from_env().load_db()

    logger.info('Loading localities.')
    WOFLocalityRepo.from_env().load_db()


@task
def build_indexes(ctx):

    state_idx = USStateIndex()
    state_idx.build()
    state_idx.save(US_STATE_PATH)

    city_idx = USCityIndex()
    city_idx.build()
    city_idx.save(US_CITY_PATH)
