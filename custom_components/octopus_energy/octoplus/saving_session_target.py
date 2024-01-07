import asyncio
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfEnergy
)

from . import (
  current_saving_sessions_event,
  get_next_saving_sessions_event,
  get_saving_session_consumption_dates,
  get_saving_session_target
)

from ..coordinators.saving_sessions import SavingSessionsCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

from ..const import REFRESH_RATE_IN_MINUTES_OCTOPLUS_SAVING_SESSION_TARGET
from ..utils.requests import calculate_next_refresh
from ..api_client import ApiException, OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

class OctopusEnergySavingSessionTarget(CoordinatorEntity, RestoreSensor):
  """Sensor for determining the target for the current or next saving session."""

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str, client: OctopusEnergyApiClient, mpan: str, serial_number: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._client = client
    self._state = None
    self._consumption_data = None
    self._attributes = {
      "mpan": mpan,
      "serial_number": serial_number,
      "saving_session_target_start": None,
      "saving_session_target_end": None,
      "is_incomplete_calculation": None,
      "consumption_items": None,
      "total_target": None,
      "targets": None,
    }
    self._next_refresh = None

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_saving_session_target"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy {self._account_id} Octoplus Saving Session Target"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfEnergy.KILO_WATT_HOUR

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @property
  def should_poll(self) -> bool:
    return True

  async def async_update(self):
    await super().async_update()

    if not self.enabled:
      return
    
    current = utcnow()
    saving_session: SavingSessionsCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    if (saving_session is not None):

      all_saving_sessions = saving_session.available_events + saving_session.joined_events
      target_saving_session = current_saving_sessions_event(current, saving_session.joined_events)
      if (target_saving_session is None):
        target_saving_session = get_next_saving_sessions_event(current, saving_session.joined_events)

      if (target_saving_session is not None):
        if (self._next_refresh is None or current >= self._next_refresh) and (self._consumption_data is None or self._attributes["is_incomplete_calculation"] != False):
          consumption_dates = get_saving_session_consumption_dates(target_saving_session, all_saving_sessions)

          try:
            requests = []
            for consumption_date in consumption_dates:
              requests.append(self._client.async_get_electricity_consumption(self._attributes["mpan"],
                                                                             self._attributes["serial_number"],
                                                                             consumption_date.start,
                                                                             consumption_date.end))
            consumption_data = await asyncio.gather(*requests)
            self._consumption_data = [
              x
              for xs in consumption_data
              for x in xs
            ]

            self._request_attempts = 1
            self._last_retrieved = current
            self._next_refresh = calculate_next_refresh(current, self._request_attempts, REFRESH_RATE_IN_MINUTES_OCTOPLUS_SAVING_SESSION_TARGET)
            _LOGGER.info('Consumption data was refreshed successfully')
          except Exception as e:
            if isinstance(e, ApiException) == False:
              _LOGGER.error(e)
              raise
            
            self._request_attempts = self._request_attempts + 1
            self._next_refresh = calculate_next_refresh(
              self._last_retrieved if self._last_retrieved is not None else current,
              self._request_attempts,
              REFRESH_RATE_IN_MINUTES_OCTOPLUS_SAVING_SESSION_TARGET
            )
            _LOGGER.warning(f'Failed to retrieve saving session target data - using cached data. Next attempt at {self._next_refresh}')

        target = get_saving_session_target(current, target_saving_session, self._consumption_data if self._consumption_data is not None else [])
        if (target is not None and target.current_target is not None):
          self._state = target.current_target.target
          self._attributes["saving_session_target_start"] = target.current_target.start
          self._attributes["saving_session_target_end"] = target.current_target.end
          self._attributes["is_incomplete_calculation"] = target.current_target.is_incomplete_calculation
          self._attributes["consumption_items"] = target.current_target.consumption_items
          self._attributes["total_target"] = target.total_target
          self._attributes["targets"] = list(map(lambda target: {
            "start": target.start,
            "end": target.end,
            "target": target.target,
            "is_incomplete_calculation": target.is_incomplete_calculation
          }, target.targets))
        else:
          self._attributes["saving_session_target_start"] = None
          self._attributes["saving_session_target_end"] = None
          self._attributes["is_incomplete_calculation"] = None
          self._attributes["consumption_items"] = None
          self._attributes["total_target"] = None
          self._attributes["targets"] = None

      else:
        self._state = None
        self._attributes["saving_session_target_start"] = None
        self._attributes["saving_session_target_end"] = None
        self._attributes["is_incomplete_calculation"] = None
        self._attributes["consumption_items"] = None
        self._attributes["total_target"] = None
        self._attributes["targets"] = None

    if saving_session is not None:
      self._attributes["data_last_retrieved"] = saving_session.last_retrieved

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
    
    _LOGGER.debug(f'Restored state: {self._state}')
