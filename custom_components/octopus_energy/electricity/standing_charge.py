import logging

from homeassistant.core import HomeAssistant

from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityCurrentStandingCharge(CoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current standing charge."""

  def __init__(self, hass: HomeAssistant, coordinator, tariff_code, meter, point):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._tariff_code = tariff_code

    self._state = None
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f'octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_current_standing_charge'
    
  @property
  def name(self):
    """Name of the sensor."""
    return f'Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Current Standing Charge'

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

  @property
  def unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "GBP"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """Retrieve the latest electricity standing charge"""
    _LOGGER.debug('Updating OctopusEnergyElectricityCurrentStandingCharge')

    standard_charge_result = self.coordinator.data.standing_charge if self.coordinator is not None and self.coordinator.data is not None else None
    
    if standard_charge_result is not None:
      self._latest_date = standard_charge_result["valid_from"]
      self._state = standard_charge_result["value_inc_vat"] / 100

      # Adjust our period, as our gas only changes on a daily basis
      self._attributes["valid_from"] = standard_charge_result["valid_from"]
      self._attributes["valid_to"] = standard_charge_result["valid_to"]
    else:
      self._state = None

    return self._state

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = state.state
      self._attributes = {}
      for x in state.attributes.keys():
        self._attributes[x] = state.attributes[x]
    
      _LOGGER.debug(f'Restored OctopusEnergyElectricityCurrentStandingCharge state: {self._state}')