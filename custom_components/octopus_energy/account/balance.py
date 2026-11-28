import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass
)

from . import get_account_balance_in_pounds
from ..coordinators.account_balance import AccountBalanceCoordinatorResult
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyAccountBalance(CoordinatorEntity, RestoreSensor):
  """Sensor for the current balance of the account, where positive is in credit and negative is in debit"""

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)

    self._account_id = account_id
    self._state: float | None = None
    self._attributes = {}

    self.entity_id = generate_entity_id("sensor.{}", self.unique_id, hass=hass)

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_account_balance"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Account Balance ({self._account_id})"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return "GBP"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def native_value(self):
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    result: AccountBalanceCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if result is not None and result.data is not None:
      self._state = get_account_balance_in_pounds(result.data.balance)
      self._attributes["last_transaction_date"] = result.data.last_transaction_date

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

      _LOGGER.debug(f'Restored OctopusEnergyAccountBalance state: {self._state}')
