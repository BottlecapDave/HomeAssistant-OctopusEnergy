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

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.greenness_forecast import GreennessForecastCoordinatorResult
from . import get_current_and_next_forecast, greenness_forecast_to_dictionary

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGreennessForecastHighlighted(CoordinatorEntity, BinarySensorEntity, RestoreEntity):
  """Sensor for determining if the current forecast has been highlighted."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._state = None
    self._attributes = {
      "current": None,
      "next_start": None,
      "next_end": None,
    }
    self._last_updated = None

    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_greenness_forecast_highlighted"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Greenness Forecast Highlighted ({self._account_id})"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:leaf"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if current forecast is highlighted by OE."""
    current = now()
    self._state = False
    result: GreennessForecastCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    forecast = result.forecast if result is not None else None
    if (forecast is not None):
      _LOGGER.debug(f"Updating OctopusEnergyGreennessForecastHighlighted for '{self._account_id}'")

      self._attributes = {
        "current": None,
        "next_start": None,
        "next_end": None,
      }

      current_and_next = get_current_and_next_forecast(current, forecast, True)
      if current_and_next is not None:
        self._attributes["current"] = greenness_forecast_to_dictionary(current_and_next.current) if current_and_next.current is not None else None

        if current_and_next.next is not None:
          self._attributes["next_start"] = current_and_next.next.start
          self._attributes["next_end"] = current_and_next.next.end

        self._state = current_and_next.current is not None

    self._attributes = dict_to_typed_dict(self._attributes)
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
    
    _LOGGER.debug(f'Restored OctopusEnergyGreennessForecastHighlighted state: {self._state}')
