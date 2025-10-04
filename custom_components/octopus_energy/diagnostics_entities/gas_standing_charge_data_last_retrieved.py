from .base import OctopusEnergyBaseDataLastRetrieved
from ..gas.base import OctopusEnergyGasSensor

class OctopusEnergyGasCurrentStandingChargeDataLastRetrieved(OctopusEnergyGasSensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the standing charge data was last retrieved."""

  def __init__(self, hass, coordinator, meter, point):
    """Init sensor."""
    self._mprn = point["mprn"]
    self._serial_number = meter["serial_number"]
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_standing_charge_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Standing Charge Data Last Retrieved Gas ({self._serial_number}/{self._mprn})"