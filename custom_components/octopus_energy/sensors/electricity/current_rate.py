from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass
)

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityCurrentRate(CoordinatorEntity, OctopusEnergyElectricitySensor):
  """Sensor for displaying the current rate."""

  def __init__(self, coordinator, meter, point, electricity_price_cap):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, meter, point)

    self._state = None
    self._last_updated = None
    self._electricity_price_cap = electricity_price_cap

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_current_rate"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Current Rate"

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
    """The state of the sensor."""
    # Find the current rate. We only need to do this every half an hour
    now = utcnow()
    if (self._last_updated is None or self._last_updated < (now - timedelta(minutes=30)) or (now.minute % 30) == 0):
      _LOGGER.debug(f"Updating OctopusEnergyElectricityCurrentRate for '{self._mpan}/{self._serial_number}'")

      current_rate = None
      if self.coordinator.data != None:
        rate = self.coordinator.data[self._mpan] if self._mpan in self.coordinator.data else None
        if rate != None:
          for period in rate:
            if now >= period["valid_from"] and now <= period["valid_to"]:
              current_rate = period
              break

      if current_rate != None:
        ratesAttributes = list(map(lambda x: {
          "from": x["valid_from"],
          "to":   x["valid_to"],
          "rate": x["value_inc_vat"],
          "is_capped": x["is_capped"]
        }, rate))
        self._attributes = {
          "rate": current_rate,
          "is_export": self._is_export,
          "is_smart_meter": self._is_smart_meter,
          "rates": ratesAttributes
        }

        if self._electricity_price_cap is not None:
          self._attributes["price_cap"] = self._electricity_price_cap
        
        self._state = current_rate["value_inc_vat"] / 100
      else:
        self._state = None
        self._attributes = {}

      self._last_updated = now

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
    
      _LOGGER.debug(f'Restored OctopusEnergyElectricityCurrentRate state: {self._state}')