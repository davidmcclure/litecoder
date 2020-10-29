

import pytest

from litecoder.usa import USCityIndex, USStateIndex


@pytest.fixture(scope='session')
def city_idx():
    city_idx = USCityIndex()
    city_idx.load()
    return city_idx


@pytest.fixture(scope='session')
def state_idx():
    state_idx = USStateIndex()
    state_idx.load()
    return state_idx
