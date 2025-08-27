import logging
import pytz
import pytest

from homeassistant.util.dt import (set_default_time_zone)

_LOGGER = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
  yield

  _LOGGER.info('Resetting timezone to UTC')
  set_default_time_zone(pytz.timezone('UTC'))