

import pytest

from litecoder.usa import USCityIndex, USStateIndex


@pytest.fixture(scope='session')
def city_idx():
    return USCityIndex.load()


@pytest.fixture(scope='session')
def state_idx():
    return USStateIndex.load()
