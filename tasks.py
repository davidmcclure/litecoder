

from invoke import task

from litecoder.models import BaseModel
from litecoder.sources import WOFRegionsRepo, WOFLocalitiesRepo
from litecoder import logger

@task
def load_db(ctx):

    BaseModel.reset()

    logger.info('Loading regions.')
    WOFRegionsRepo.from_env().load_db()

    logger.info('Loading localities.')
    WOFLocalitiesRepo.from_env().load_db()
