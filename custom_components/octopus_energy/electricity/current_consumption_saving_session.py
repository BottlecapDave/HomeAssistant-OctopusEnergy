import logging
from custom_components.octopus_energy.octoplus import current_saving_sessions_event

from homeassistant.core import HomeAssistant, callback

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

from homeassistant.util.dt import (now)

from ..coordinators.current_consumption import CurrentConsumptionCoordinatorResult
from ..coordinators.saving_sessions import SavingSessionsCoordinatorResult
from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCurrentElectricityConsumptionSavingSession(CoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the current electricity consumption for the current saving session."""

  def __init__(self, hass: HomeAssistant, coordinator, saving_session_coordinator, meter, point):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._state = None
    self._last_reset = None
    
    self._saving_session_coordinator = saving_session_coordinator

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}_octoplus_saving_session_current_consumption"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Saving Session Current Consumption Electricity ({self._serial_number}/{self._mpan})"
  
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
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current days accumulative consumption"""
    current = now()
    consumption_result: CurrentConsumptionCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    saving_session: SavingSessionsCoordinatorResult = self._saving_session_coordinator.data if self._saving_session_coordinator is not None else None
    consumption_data = consumption_result.data if consumption_result is not None else None

    self._state = None
    if (saving_session is not None and consumption_data is not None):
      target_saving_session = current_saving_sessions_event(current, saving_session.joined_events)
      if (target_saving_session is not None):
        try:
          consumption = next(r for r in consumption_data if r["start"] == target_saving_session.start and r["end"] == target_saving_session.end)
          if consumption is not None:
            self._state = consumption["consumption"]
        except StopIteration:
          self._state = None

    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None and self._state is None:
      self._state = None if state.state == "unknown" else state.state
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyCurrentElectricityConsumptionSavingSession state: {self._state}')