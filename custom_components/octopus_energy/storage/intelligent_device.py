import logging
from homeassistant.helpers import storage

from ..api_client.intelligent_device import IntelligentDevice

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_intelligent_devices(hass, account_id: str) -> list[IntelligentDevice]:
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_intelligent_devices")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached intelligent device data for {account_id}")
      devices = []
      for item in data:
        devices.append(IntelligentDevice(
          item["id"],
          item["provider"],
          item["make"],
          item["model"],
          item["vehicleBatterySizeInKwh"],
          item["chargePointPowerInKw"],
          item["device_type"]
        ))

      return devices
  except:
    return []
  
async def async_save_cached_intelligent_devices(hass, account_id: str, intelligent_devices: list[IntelligentDevice]):
  if intelligent_devices is not None:
    store = storage.Store(hass, "1", f"octopus_energy.{account_id}_intelligent_devices")
    await store.async_save(list(map(lambda x: x.to_dict(), intelligent_devices)))
    _LOGGER.debug(f"Saved intelligent device data for ({account_id})")