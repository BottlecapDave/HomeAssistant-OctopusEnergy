from .base import OctopusEnergyBaseDataLastRetrieved

class OctopusEnergyHeatPumpDataLastRetrieved(OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the heat pump data was last retrieved."""

  def __init__(self, hass, coordinator, account_id: str, heat_pump_id: str):
    """Init sensor."""
    self._account_id = account_id
    self._heat_pump_id = heat_pump_id
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._heat_pump_id}_heat_pump_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Heat Pump Data Last Retrieved ({self._heat_pump_id}/{self._account_id})"