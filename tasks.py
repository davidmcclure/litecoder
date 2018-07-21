

from invoke import task

from litecoder.db import BaseModel


@task
def reset_db(ctx):
    BaseModel.reset()


@task
def load_db(ctx, path):
    City.load(path)
