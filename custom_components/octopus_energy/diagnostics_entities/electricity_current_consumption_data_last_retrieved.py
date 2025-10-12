from .base import OctopusEnergyBaseDataLastRetrieved
from ..electricity.base import OctopusEnergyElectricitySensor

class OctopusEnergyElectricityCurrentConsumptionDataLastRetrieved(OctopusEnergyElectricitySensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the current consumption data was last retrieved."""

  def __init__(self, hass, coordinator, meter, point):
    """Init sensor."""
    self._mpan = point["mpan"]
    self._serial_number = meter["serial_number"]
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_current_consumption_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Consumption Data Last Retrieved Electricity ({self._serial_number}/{self._mpan})"