import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorStateClass
)

from ..coordinators.wheel_of_fortune import WheelOfFortuneSpinsCoordinatorResult
from ..api_client import OctopusEnergyApiClient
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyWheelOfFortuneElectricitySpins(CoordinatorEntity, RestoreSensor):
  """Sensor for current wheel of fortune spins for electricity"""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, account_id: str):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
  
    self._account_id = account_id
    self._client = client
    self._state = None
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_wheel_of_fortune_spins_electricity"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Wheel Of Fortune Spins Electricity ({self._account_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:star-circle"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def state(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    result: WheelOfFortuneSpinsCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if result is not None and result.spins is not None:
      self._state = result.spins.electricity
    
    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    last_sensor_state = await self.async_get_last_sensor_data()
    
    if state is not None and last_sensor_state is not None and self._state is None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) else last_sensor_state.native_value
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyWheelOfFortuneElectricitySpins state: {self._state}')

  @callback
  async def async_spin_wheel(self):
    """Spin the wheel of fortune"""

    result = await self._client.async_spin_wheel_of_fortune(self._account_id, True)
    return {
      "amount_won_in_pence": result
    }