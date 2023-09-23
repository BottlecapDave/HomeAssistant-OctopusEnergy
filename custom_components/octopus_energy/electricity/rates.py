import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityRates(OctopusEnergyElectricitySensor, EventEntity, RestoreEntity):
  """Sensor for displaying the current rate."""

  def __init__(self, hass: HomeAssistant, meter, point):
    """Init sensor."""
    # Pass coordinator to base class
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_updated = None

    self._attr_event_types = [f'octopus_energy_electricity_{self._mpan}_rates']

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_rates"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Rates"

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
    
      _LOGGER.debug(f'Restored OctopusEnergyElectricityRates state: {self._state}')

  async def async_added_to_hass(self) -> None:
    """Register callbacks."""
    self.hass.bus.async_listen(self._attr_event_types[0], self._async_handle_event)

  @callback
  def _async_handle_event(self, _) -> None:
    """Handle the demo button event."""
    self._trigger_event(self._attr_event_types[0])
    self.async_write_ha_state()