from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo

from ..const import (
  DOMAIN,
)

class OctopusEnergyGreennessForecastSensor:
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})
  
  def __init__(self, account_id: str):
    """Init sensor"""

    self._attr_device_info = DeviceInfo(
      identifiers={
        (DOMAIN, f"greenness-forecast-{account_id}")
      },
      name=f"Greenness Forecast ({account_id})",
      connections=set(),
      entry_type=DeviceEntryType.SERVICE,
    )