from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)

from .base import (OctopusEnergyGasSensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGasCurrentRate(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, coordinator, tariff_code, meter, point, gas_price_cap):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyGasSensor.__init__(self, hass, meter, point)

    self._tariff_code = tariff_code
    self._gas_price_cap = gas_price_cap

    self._state = None
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f'octopus_energy_gas_{self._serial_number}_{self._mprn}_current_rate';
    
  @property
  def name(self):
    """Name of the sensor."""
    return f'Gas {self._serial_number} {self._mprn} Current Rate'
  
  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

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
    return "GBP/kWh"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state(self):
    """Retrieve the latest gas price"""

    current = now()
    if (self._latest_date is None or (self._latest_date + timedelta(days=1)) < current) or self._state is None:
      _LOGGER.debug('Updating OctopusEnergyGasCurrentRate')

      rates = self.coordinator.data
      
      current_rate = None
      if rates is not None:
        for period in rates:
          if current >= period["valid_from"] and current <= period["valid_to"]:
            current_rate = period
            break

      if current_rate is not None:
        self._latest_date = rates[0]["valid_from"]
        self._state = current_rate["value_inc_vat"] / 100

        # Adjust our period, as our gas only changes on a daily basis
        current_rate["valid_from"] = rates[0]["valid_from"]
        current_rate["valid_to"] = rates[-1]["valid_to"]
        self._attributes = current_rate

        if self._gas_price_cap is not None:
          self._attributes["price_cap"] = self._gas_price_cap
      else:
        self._state = None
        self._attributes = {}

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
    
      _LOGGER.debug(f'Restored OctopusEnergyGasCurrentRate state: {self._state}')