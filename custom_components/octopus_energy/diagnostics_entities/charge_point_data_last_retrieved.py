from .base import OctopusEnergyBaseDataLastRetrieved
from ..charge_point.base import BaseOctopusEnergyChargePointSensor
from ..api_client.charge_point import OnboardedChargePoint

class OctopusEnergyChargePointDataLastRetrieved(BaseOctopusEnergyChargePointSensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the charge point data was last retrieved."""

  def __init__(self, hass, coordinator, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint):
    """Init sensor."""
    self._account_id = account_id
    self._charge_point_id = charge_point_id
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point)
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._charge_point_id}_charge_point_data_last_retrieved"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Charge Point Data Last Retrieved ({self._charge_point_id}/{self._account_id})"
