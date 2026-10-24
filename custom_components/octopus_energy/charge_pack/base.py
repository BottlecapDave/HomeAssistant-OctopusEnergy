from homeassistant.helpers.device_registry import DeviceInfo

from ..const import (
  DOMAIN,
)
from ..api_client.charge_pack import ChargePackDevice

class OctopusEnergyChargePackSensor:

  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, device: ChargePackDevice):
    """Init sensor"""

    self._device = device
    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, f"charge_pack_{device.id}")
      },
      name=f"{device.display_name} (Charge Pack)",
      connections=set(),
      manufacturer=device.make,
      model=device.model
    )
