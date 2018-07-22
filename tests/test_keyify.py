

import pytest

from litecoder.usa import keyify


@pytest.mark.parametrize('text,key', [

    # Downcase
    ('BOSTON', 'boston'),

    # Strip
    ('  Boston  ', 'boston'),

    # Remove periods
    ('Washington D.C.', 'washington dc'),

    # Comma -> space
    ('Boston,MA', 'boston ma'),

    # Dash -> space
    ('La-La Land', 'la la land'),

    # 2+ whitespace -> 1 space
    ('Boston  MA   USA', 'boston ma usa'),

])
def test_keyify(text, key):
    assert keyify(text) == key
