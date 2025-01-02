from datetime import datetime, timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.util.dt import (utcnow)
from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
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
  current_octoplus_sessions_event,
  get_filtered_consumptions,
  get_next_octoplus_sessions_event,
  get_octoplus_session_consumption_dates,
  get_octoplus_session_target
)

from ..coordinators.saving_sessions import SavingSessionsCoordinatorResult
from ..utils.attributes import dict_to_typed_dict
from ..api_client.saving_sessions import SavingSession

from ..electricity.base import OctopusEnergyElectricitySensor
from ..coordinators import MultiCoordinatorEntity
from ..coordinators.previous_consumption_and_rates import PreviousConsumptionCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergySavingSessionBaseline(MultiCoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for determining the baseline for the current or next saving session."""

  _unrecorded_attributes = frozenset({
    "mpan",
    "serial_number",
    "start",
    "end",
    "consumption_items",
    "baselines",
    "data_last_retrieved"
  })

  def __init__(self, hass: HomeAssistant, saving_session_coordinator, previous_rates_and_consumption_coordinator, meter, point, mock_baseline):
    """Init sensor."""

    MultiCoordinatorEntity.__init__(self, saving_session_coordinator, [previous_rates_and_consumption_coordinator])
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._previous_rates_and_consumption_coordinator = previous_rates_and_consumption_coordinator
    self._state = None
    self._attributes = {
      "mpan": self._mpan,
      "serial_number": self._serial_number,
      "start": None,
      "end": None,
      "is_incomplete_calculation": None,
      "consumption_items": None,
      "total_baseline": None,
      "baselines": None,
    }
    self._consumption_data = None
    self._mock_baseline = mock_baseline

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_octoplus_saving_session_baseline"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Saving Session Baseline {self._export_name_addition}Electricity ({self._serial_number}/{self._mpan})"
  
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
    
    current: datetime = utcnow()
    saving_session: SavingSessionsCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    previous_consumption: PreviousConsumptionCoordinatorResult = self._previous_rates_and_consumption_coordinator.data if self._previous_rates_and_consumption_coordinator is not None else None
    if saving_session is not None and previous_consumption is not None:

      all_saving_sessions = saving_session.available_events + saving_session.joined_events
      target_saving_session = current_octoplus_sessions_event(current, saving_session.joined_events)
      if (target_saving_session is None):
        target_saving_session = get_next_octoplus_sessions_event(current, saving_session.joined_events)

      if (target_saving_session is None and self._mock_baseline == True):
        mock_saving_session_start = current.replace(minute=0, second=0, microsecond=0)
        target_saving_session = SavingSession('1', '2', mock_saving_session_start, mock_saving_session_start + timedelta(hours=1), 0)

      if (target_saving_session is not None):
        consumption_dates = get_octoplus_session_consumption_dates(target_saving_session, all_saving_sessions)
        self._consumption_data = get_filtered_consumptions(previous_consumption.historic_weekday_consumption if target_saving_session.start.weekday() < 5 else previous_consumption.historic_weekend_consumption, consumption_dates)

      target = get_octoplus_session_target(current, target_saving_session, self._consumption_data if self._consumption_data is not None else [])
      if (target is not None and target.current_target is not None):
        self._state = target.current_target.baseline
        self._attributes["start"] = target.current_target.start
        self._attributes["end"] = target.current_target.end
        self._attributes["is_incomplete_calculation"] = target.current_target.is_incomplete_calculation
        self._attributes["consumption_items"] = target.current_target.consumption_items
        self._attributes["total_baseline"] = target.total_baseline
        self._attributes["baselines"] = list(map(lambda target: {
          "start": target.start,
          "end": target.end,
          "baseline": target.baseline,
          "is_incomplete_calculation": target.is_incomplete_calculation
        }, target.baselines))
      else:
        self._attributes["start"] = None
        self._attributes["end"] = None
        self._attributes["is_incomplete_calculation"] = None
        self._attributes["consumption_items"] = None
        self._attributes["total_baseline"] = None
        self._attributes["baselines"] = None

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
    _LOGGER.debug(f'Restored state: {self._state}')
