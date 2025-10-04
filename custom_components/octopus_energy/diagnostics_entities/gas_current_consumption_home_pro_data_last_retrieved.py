from .base import OctopusEnergyBaseDataLastRetrieved
from ..gas.base import OctopusEnergyGasSensor

class OctopusEnergyGasCurrentConsumptionHomeProDataLastRetrieved(OctopusEnergyGasSensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the current consumption home pro data was last retrieved."""

  def __init__(self, hass, coordinator, meter, point):
    """Init sensor."""
    self._mprn = point["mprn"]
    self._serial_number = meter["serial_number"]
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_home_pro_current_consumption_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Home Pro Current Consumption Data Last Retrieved Gas ({self._serial_number}/{self._mprn})"