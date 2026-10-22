import logging
from homeassistant.helpers import storage

from ..api_client.charge_pack import ChargePackDevice, ChargePackDispatch

_LOGGER = logging.getLogger(__name__)

async def async_load_cached_charge_pack_devices(hass, account_id: str) -> list[ChargePackDevice]:
  store = storage.Store(hass, "1", f"octopus_energy.{account_id}_charge_pack_devices")
  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached charge pack device data for {account_id}")
      return [ChargePackDevice.from_dict(item) for item in data]
  except:
    pass
  return []

async def async_save_cached_charge_pack_devices(hass, account_id: str, devices: list[ChargePackDevice]):
  if devices is not None:
    store = storage.Store(hass, "1", f"octopus_energy.{account_id}_charge_pack_devices")
    await store.async_save([device.to_dict() for device in devices])
    _LOGGER.debug(f"Saved charge pack device data for ({account_id})")

async def async_load_cached_charge_pack_history(hass, device_id: str) -> list[ChargePackDispatch]:
  """The dispatches that have started (see charge_pack.update_history)."""
  store = storage.Store(hass, "1", f"octopus_energy.charge_pack_history_{device_id}")
  try:
    data = await store.async_load()
    if data is not None:
      return [ChargePackDispatch.from_dict(item) for item in data.get("history") or []]
  except:
    _LOGGER.warning(f"Failed to load the charge pack history for {device_id}")
  return []

async def async_save_cached_charge_pack_history(hass, device_id: str, history: list[ChargePackDispatch]):
  store = storage.Store(hass, "1", f"octopus_energy.charge_pack_history_{device_id}")
  await store.async_save({"history": [d.to_dict() for d in history]})
  _LOGGER.debug(f"Saved charge pack history for {device_id}")
