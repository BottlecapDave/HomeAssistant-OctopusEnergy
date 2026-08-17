from .base import OctopusEnergyBaseDataLastRetrieved
from ..gas.base import OctopusEnergyGasSensor

class OctopusEnergyGasPreviousConsumptionAndRatesDataLastRetrieved(OctopusEnergyGasSensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time previous consumption and rate data was last retrieved."""

  def __init__(self, hass, coordinator, meter, point):
    """Init sensor."""
    self._mprn = point["mprn"]
    self._serial_number = meter["serial_number"]
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator, generate_legacy_entity_id=False)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_consumption_rates_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return "Previous Consumption and Rates Data Last Retrieved"