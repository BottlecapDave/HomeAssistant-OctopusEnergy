import logging

from homeassistant.helpers import storage

from ..const import STORAGE_ACCOUNT_DEBUG_OVERRIDE_NAME, STORAGE_METER_DEBUG_OVERRIDE_NAME
from ..utils import Tariff

_LOGGER = logging.getLogger(__name__)

class MeterDebugOverride():

  def __init__(self, tariff: Tariff):
    self.tariff = tariff

async def async_get_meter_debug_override(hass, mpan_mprn: str, serial_number: str) -> MeterDebugOverride | None:
  storage_key = STORAGE_METER_DEBUG_OVERRIDE_NAME.format(mpan_mprn, serial_number)
  store = storage.Store(hass, "1", storage_key)

  try:
    data = await store.async_load()
    if data is not None:
      debug = MeterDebugOverride(
        Tariff(data["product_code"], data["tariff_code"]) if "tariff_code" in data and "product_code" in data else None
      )

      _LOGGER.info(f"Debug overrides discovered {mpan_mprn}/{serial_number} - {debug}")

      return debug

  except:
    return None
  
  return None

class AccountDebugOverride():

  def __init__(self, mock_intelligent_controls: bool, mock_saving_session_baseline: bool, mock_heat_pump: bool):
    self.mock_intelligent_controls = mock_intelligent_controls
    self.mock_saving_session_baseline = mock_saving_session_baseline
    self.mock_heat_pump = mock_heat_pump

async def async_get_account_debug_override(hass, account_id: str) -> AccountDebugOverride | None:
  storage_key = STORAGE_ACCOUNT_DEBUG_OVERRIDE_NAME.format(account_id)
  store = storage.Store(hass, "1", storage_key)

  try:
    data = await store.async_load()
    if data is not None:
      debug = AccountDebugOverride(
        data["mock_intelligent_controls"] == True if "mock_intelligent_controls" in data else False,
        data["mock_saving_session_baseline"] == True if "mock_saving_session_baseline" in data else False,
        data["mock_heat_pump"] == True if "mock_heat_pump" in data else False,
      )

      _LOGGER.info(f"Debug overrides discovered {account_id} - {debug}")

      return debug

  except:
    return None
  
  return None