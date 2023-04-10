from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
    SensorDeviceClass
)

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityPreviousRate(CoordinatorEntity, OctopusEnergyElectricitySensor):
  """Sensor for displaying the previous rate."""

  def __init__(self, coordinator, meter, point):
    """Init sensor."""
    # Pass coordinator to base class
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, meter, point)

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_rate"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Previous Rate"

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
    # Find the previous rate. We only need to do this every half an hour
    now = utcnow()
    if (self._last_updated is None or self._last_updated < (now - timedelta(minutes=30)) or (now.minute % 30) == 0):
      _LOGGER.debug(f"Updating OctopusEnergyElectricityPreviousRate for '{self._mpan}/{self._serial_number}'")

      target = now - timedelta(minutes=30)

      previous_rate = None
      if self.coordinator.data != None:
        rate = self.coordinator.data[self._mpan] if self._mpan in self.coordinator.data else None
        if rate != None:
          for period in rate:
            if target >= period["valid_from"] and target <= period["valid_to"]:
              previous_rate = period
              break

      if previous_rate != None:
        self._attributes = {
          "rate": previous_rate,
          "is_export": self._is_export,
          "is_smart_meter": self._is_smart_meter
        }

        self._state = previous_rate["value_inc_vat"] / 100
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
    
      _LOGGER.debug(f'Restored OctopusEnergyElectricityPreviousRate state: {self._state}')