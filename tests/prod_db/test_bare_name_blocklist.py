

import pytest

from litecoder.usa import USCityIndex


# TODO: Possible to speed this up?
def test_bare_name_bloclist():
    """Blocklisted bare names should be omitted from index.
    """
    idx = USCityIndex(bare_name_blocklist=['Washington', 'New York'])
    idx.build()

    blocked = (
        'Washington',
        'washington',
        'Washington, USA',
        'New York',
        'new york',
        'New York, USA'
    )

    for query in blocked:
        assert not idx[query]

    assert idx['Washington DC'][0].data.wof_id == 85931779
    assert idx['New York, NY'][0].data.wof_id == 85977539
