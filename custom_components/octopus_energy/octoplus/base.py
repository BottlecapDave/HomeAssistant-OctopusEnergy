from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyOctoplusSensor:
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})
  
  def __init__(self, account_id: str):
    """Init sensor"""

    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, f"octoplus-{account_id}")
      },
      name=f"Octoplus ({account_id})",
      connections=set(),
      entry_type=DeviceEntryType.SERVICE,
    )