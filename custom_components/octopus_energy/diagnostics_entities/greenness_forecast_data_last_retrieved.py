from .base import OctopusEnergyBaseDataLastRetrieved

class OctopusEnergyGreennessForecastDataLastRetrieved(OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the greenness forecast data was last retrieved."""

  def __init__(self, hass, coordinator, account_id):
    """Init sensor."""
    self._account_id = account_id
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_greenness_forecast_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Greenness Forecast Data Last Retrieved ({self._account_id})"