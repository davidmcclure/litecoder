

import os
import logging
import sys


LITECODER_ENV = os.environ.get('LITECODER_ENV')

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

US_STATE_PATH = os.path.join(DATA_DIR, 'us-states.db')

US_CITY_PATH = os.path.join(DATA_DIR, 'us-cities.db')


logging.basicConfig(
    format='%(asctime)s | %(levelname)s : %(message)s',
    stream=sys.stdout,
    level=logging.INFO,
)

logger = logging.getLogger('litecoder')
