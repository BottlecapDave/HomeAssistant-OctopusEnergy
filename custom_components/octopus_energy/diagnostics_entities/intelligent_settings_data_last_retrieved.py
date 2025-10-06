from .base import OctopusEnergyBaseDataLastRetrieved
from ..intelligent.base import OctopusEnergyIntelligentSensor
from ..api_client.intelligent_device import IntelligentDevice

class OctopusEnergyIntelligentSettingsDataLastRetrieved(OctopusEnergyIntelligentSensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the intelligent settings data was last retrieved."""

  def __init__(self, hass, coordinator, account_id: str, device: IntelligentDevice):
    """Init sensor."""
    self._account_id = account_id
    self._device_id = device.id
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._device_id}_intelligent_settings_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Settings Data Last Retrieved ({self._device_id})"