import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (OctopusEnergyElectricitySensor)
from ..const import EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_OVERRIDE_RATES

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityPreviousConsumptionOverrideRates(OctopusEnergyElectricitySensor, EventEntity, RestoreEntity):
  """Sensor for displaying the previous consumption override's rates."""

  def __init__(self, hass: HomeAssistant, meter, point):
    """Init sensor."""
    # Pass coordinator to base class
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._hass = hass
    self._state = None
    self._last_updated = None

    self._attr_event_types = [EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_OVERRIDE_RATES]

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_consumption_override_rates"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Previous Consumption Override Rates"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

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
    
      _LOGGER.debug(f'Restored OctopusEnergyElectricityPreviousConsumptionOverrideRates state: {self._state}')

  async def async_added_to_hass(self) -> None:
    """Register callbacks."""
    self._hass.bus.async_listen(self._attr_event_types[0], self._async_handle_event)

  @callback
  def _async_handle_event(self, event) -> None:
    if (event.data is not None and "mpan" in event.data and event.data["mpan"] == self._mpan):
      self._trigger_event(event.event_type, event.data)
      self.async_write_ha_state()