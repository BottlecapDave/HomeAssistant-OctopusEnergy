from datetime import timedelta
import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity
)
from homeassistant.helpers.restore_state import RestoreEntity

from ..utils import is_off_peak

from .base import OctopusEnergyElectricitySensor
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityOffPeak(CoordinatorEntity, OctopusEnergyElectricitySensor, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if the current rate is off peak."""

  def __init__(self, hass: HomeAssistant, coordinator, meter, point):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)
  
    self._state = None
    self._attributes = {}
    self._last_updated = None

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_off_peak"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Off Peak"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if current rate is off peak."""
    current = now()
    rates = self.coordinator.data.rates if self.coordinator is not None and self.coordinator.data is not None else None
    if (rates is not None and (self._last_updated is None or self._last_updated < (current - timedelta(minutes=30)) or (current.minute % 30) == 0)):
      _LOGGER.debug(f"Updating OctopusEnergyElectricityOffPeak for '{self._mpan}/{self._serial_number}'")

      self._state = is_off_peak(current, rates)

      self._last_updated = current

    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
      self._attributes = dict_to_typed_dict(state.attributes)
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyElectricityOffPeak state: {self._state}')
