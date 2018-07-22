

from invoke import task

from litecoder import logger
from litecoder.sources import WOFRegionsRepo, WOFLocalitiesRepo
from litecoder.db import engine
from litecoder.models import BaseModel


@task
def reset_db(ctx):
    logger.info('Resetting database.')
    BaseModel.metadata.drop_all(engine)
    BaseModel.metadata.create_all(engine)


@task(reset_db)
def load_db(ctx):

    logger.info('Loading regions.')
    WOFRegionsRepo.from_env().load_db()

    logger.info('Loading localities.')
    WOFLocalitiesRepo.from_env().load_db()
