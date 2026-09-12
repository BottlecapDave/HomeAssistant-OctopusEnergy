import logging
from homeassistant.helpers import storage

from ..api_client.charge_point import OnboardedChargePoint

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_charge_point(hass, account_id: str, device_uuid: str) -> OnboardedChargePoint:
  store = storage.Store(hass, "2", f"octopus_energy.{account_id}_{device_uuid}_charge_point")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached charge point data for {account_id}/{device_uuid}")
      return OnboardedChargePoint.model_validate(data)
  except:
    return None

async def async_save_cached_charge_point(hass, account_id: str, device_uuid: str, charge_point: OnboardedChargePoint):
  if charge_point is not None:
    store = storage.Store(hass, "2", f"octopus_energy.{account_id}_{device_uuid}_charge_point")
    await store.async_save(charge_point.dict())
    _LOGGER.debug(f"Saved charge point data for {account_id}/{device_uuid}")
