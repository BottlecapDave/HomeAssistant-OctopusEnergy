import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
)

from ..utils.attributes import dict_to_typed_dict
from ..coordinators.fan_club_discounts import FanClubDiscountCoordinatorResult
from .base import OctopusEnergyFanClubSensor

from . import (get_current_fan_club_discount_information, get_fan_club_number)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyFanClubCurrentDiscount(CoordinatorEntity, RestoreSensor, OctopusEnergyFanClubSensor):
  """Sensor for displaying the current discount."""

  def __init__(self, hass, coordinator, account_id: str, discount_source: str):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)

    self._state = None
    self._last_updated = None
    self._account_id = account_id
    self._discount_source = discount_source

    self._attributes = {
      "source": self._discount_source,
      "start": None,
      "end": None,
      "current_day_min_rate": None,
      "current_day_max_rate": None,
      "current_day_average_rate": None
    }
    
    OctopusEnergyFanClubSensor.__init__(self, hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_fan_club_{self._account_id}_{get_fan_club_number(self._discount_source)}_current_discount"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Current Discount Fan Club ({get_fan_club_number(self._discount_source)}/{self._account_id})"

  @property
  def native_unit_of_measurement(self):
    """Unit of measurement of the sensor."""
    return "%"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes
  
  @property
  def native_value(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Retrieve the current rate for the sensor."""
    # Find the current rate. We only need to do this every half an hour
    current = now()
    discounts_result: FanClubDiscountCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    if (discounts_result is not None):
      _LOGGER.debug(f"Updating OctopusEnergyFanClubCurrentDiscount for '{self._discount_source}'")

      target_discount = None
      for discount in discounts_result.discounts:
        if discount.source == self._discount_source:
          target_discount = discount
          break

      discount_information = None
      if target_discount is not None:
        discount_information = get_current_fan_club_discount_information(target_discount.discounts, current)

      if discount_information is not None:
        self._attributes = {
          "source": self._discount_source,
          "start": discount_information["start"],
          "end": discount_information["end"],
          "current_day_min_rate": discount_information["min_discount_today"],
          "current_day_max_rate": discount_information["max_discount_today"],
          "current_day_average_rate": discount_information["average_discount_today"]
        }

        self._state = discount_information["discount"]
      else:
        self._attributes = {
          "source": self._discount_source,
          "start": None,
          "end": None,
          "current_day_min_rate": None,
          "current_day_max_rate": None,
          "current_day_average_rate": None
        }

        self._state = None

      self._last_updated = current

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
      self._attributes = dict_to_typed_dict(state.attributes, [])
      _LOGGER.debug(f'Restored OctopusEnergyFanClubCurrentDiscount state: {self._state}')