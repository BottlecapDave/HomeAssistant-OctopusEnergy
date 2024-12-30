import logging
from homeassistant.helpers import storage

from ..api_client.intelligent_device import IntelligentDevice

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_intelligent_device(hass, account_id: str) -> IntelligentDevice:
  store = storage.Store(hass, "2", f"octopus_energy.{account_id}_intelligent_device")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached intelligent device data for {account_id}")
      return IntelligentDevice(
        data["id"],
        data["provider"],
        data["make"],
        data["model"],
        data["vehicleBatterySizeInKwh"],
        data["chargePointPowerInKw"],
        data["is_charger"]
      )
  except:
    return None
  
async def async_save_cached_intelligent_device(hass, account_id: str, intelligent_device: IntelligentDevice):
  if intelligent_device is not None:
    store = storage.Store(hass, "2", f"octopus_energy.{account_id}_intelligent_device")
    await store.async_save(intelligent_device.to_dict(omit_id=False))
    _LOGGER.debug(f"Saved intelligent device data for ({account_id})")