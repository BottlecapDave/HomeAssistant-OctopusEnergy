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
  async_calculate_electricity_cost,
)

from ...api_client import (OctopusEnergyApiClient)

from .base import (OctopusEnergyElectricitySensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeElectricityCost(CoordinatorEntity, OctopusEnergyElectricitySensor):
  """Sensor for displaying the previous days accumulative electricity cost."""

  def __init__(self, coordinator, client: OctopusEnergyApiClient, tariff_code, meter, point):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyElectricitySensor.__init__(self, meter, point)

    self._client = client
    self._tariff_code = tariff_code

    self._state = None
    self._latest_date = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_accumulative_cost"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Previous Accumulative Cost"

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

    consumption_cost = await async_calculate_electricity_cost(
      self._client,
      self.coordinator.data,
      self._latest_date,
      period_from,
      period_to,
      self._tariff_code,
      self._is_smart_meter
    )

    if (consumption_cost != None):
      _LOGGER.debug(f"Calculated previous electricity consumption cost for '{self._mpan}/{self._serial_number}'...")
      self._latest_date = consumption_cost["last_calculated_timestamp"]
      self._state = consumption_cost["total"]

      self._attributes = {
        "mpan": self._mpan,
        "serial_number": self._serial_number,
        "is_export": self._is_export,
        "is_smart_meter": self._is_smart_meter,
        "tariff_code": self._tariff_code,
        "standing_charge": f'{consumption_cost["standing_charge"]}p',
        "total_without_standing_charge": f'£{consumption_cost["total_without_standing_charge"]}',
        "total": f'£{consumption_cost["total"]}',
        "last_calculated_timestamp": consumption_cost["last_calculated_timestamp"],
        "charges": consumption_cost["charges"]
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
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeElectricityCost state: {self._state}')