from .base import OctopusEnergyBaseDataLastRetrieved

class OctopusEnergyCurrentConsumptionHomeProDataLastRetrieved(OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the current consumption home pro data was last retrieved."""

  def __init__(self, hass, coordinator, is_electricity: bool, meter, point):
    """Init sensor."""
    self._mpanmprn = point["mpan"] if "mpan" in point else point["mprn"]
    self._serial_number = meter["serial_number"]
    self._is_electricity = is_electricity
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    meter_type = "electricity" if self._is_electricity else "gas"
    return f"octopus_energy_{meter_type}_{self._serial_number}_{self._mpanmprn}_home_pro_current_consumption_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    meter_type = "Electricity" if self._is_electricity else "Gas"
    return f"Home Pro Current Consumption Data Last Retrieved {meter_type} ({self._serial_number}/{self._mpanmprn})"