from datetime import timedelta
import logging

from homeassistant.util.dt import (now, as_utc)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from .. import (
  async_calculate_gas_cost,
)

from ...api_client import (OctopusEnergyApiClient)

from .base import (OctopusEnergyGasSensor)

_LOGGER = logging.getLogger(__name__)
  
class OctopusEnergyPreviousAccumulativeGasCost(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the previous days accumulative gas cost."""

  def __init__(self, coordinator, client: OctopusEnergyApiClient, tariff_code, meter, point, calorific_value):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyGasSensor.__init__(self, meter, point)

    self._client = client
    self._tariff_code = tariff_code
    self._native_consumption_units = meter["consumption_units"]

    self._state = None
    self._latest_date = None
    self._calorific_value = calorific_value

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_cost"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Previous Accumulative Cost"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.MONETARY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def unit_of_measurement(self):
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
  def should_poll(self):
    return True

  @property
  def last_reset(self):
    """Return the time when the sensor was last reset, if any."""
    return self._latest_date

  @property
  def state(self):
    """Retrieve the previously calculated state"""
    return self._state

  async def async_update(self):
    current_datetime = now()
    period_from = as_utc((current_datetime - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0))
    period_to = as_utc(current_datetime.replace(hour=0, minute=0, second=0, microsecond=0))

    consumption_cost = await async_calculate_gas_cost(
      self._client,
      self.coordinator.data,
      self._latest_date,
      period_from,
      period_to,
      {
        "tariff_code": self._tariff_code,
      },
      self._native_consumption_units,
      self._calorific_value
    )

    if (consumption_cost != None):
      _LOGGER.debug(f"Calculated previous gas consumption cost for '{self._mprn}/{self._serial_number}'...")
      self._latest_date = consumption_cost["last_calculated_timestamp"]
      self._state = consumption_cost["total"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "tariff_code": self._tariff_code,
        "standing_charge": f'{consumption_cost["standing_charge"]}p',
        "total_without_standing_charge": f'£{consumption_cost["total_without_standing_charge"]}',
        "total": f'£{consumption_cost["total"]}',
        "last_calculated_timestamp": consumption_cost["last_calculated_timestamp"],
        "charges": consumption_cost["charges"],
        "calorific_value": self._calorific_value
      }

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

      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasCost state: {self._state}')