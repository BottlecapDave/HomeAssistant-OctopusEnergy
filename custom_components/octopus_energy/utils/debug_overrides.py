import logging

from homeassistant.helpers import storage

from ..const import STORAGE_METER_DEBUG_OVERRIDE_NAME
from ..utils import Tariff

_LOGGER = logging.getLogger(__name__)

class DebugOverride():

  def __init__(self, tariff: Tariff, mock_intelligent_controls: bool, mock_saving_session_baseline: bool):
    self.tariff = tariff
    self.mock_intelligent_controls = mock_intelligent_controls
    self.mock_saving_session_baseline = mock_saving_session_baseline

async def async_get_debug_override(hass, mpan_mprn: str, serial_number: str) -> DebugOverride | None:
  storage_key = STORAGE_METER_DEBUG_OVERRIDE_NAME.format(mpan_mprn, serial_number)
  store = storage.Store(hass, "1", storage_key)

  try:
    data = await store.async_load()
    if data is not None:
      debug = DebugOverride(
        Tariff(data["product_code"], data["tariff_code"]) if "tariff_code" in data and "product_code" in data else None,
        data["mock_intelligent_controls"] == True if "mock_intelligent_controls" in data else False,
        data["mock_saving_session_baseline"] == True if "mock_saving_session_baseline" in data else False,
      )

      _LOGGER.info(f"Debug overrides discovered {mpan_mprn}/{serial_number} - {debug}")

      return debug

  except:
    return None
  
  return None