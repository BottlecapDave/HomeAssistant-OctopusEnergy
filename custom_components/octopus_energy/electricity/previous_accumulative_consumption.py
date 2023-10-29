import logging
from datetime import datetime
from homeassistant.core import HomeAssistant, callback

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
  RestoreSensor,
  SensorDeviceClass,
  SensorStateClass,
)
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR
)

from homeassistant.util.dt import (now)

from . import (
  calculate_electricity_consumption_and_cost,
)

from .base import (OctopusEnergyElectricitySensor)

from ..statistics.consumption import async_import_external_statistics_from_consumption, get_electricity_consumption_statistic_unique_id
from ..statistics.refresh import async_refresh_previous_electricity_consumption_data
from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeElectricityConsumption(CoordinatorEntity, OctopusEnergyElectricitySensor, RestoreSensor):
  """Sensor for displaying the previous days accumulative electricity reading."""

  def __init__(self, hass: HomeAssistant, client: OctopusEnergyApiClient, coordinator, tariff_code, meter, point):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self._client = client
    self._state = None
    self._tariff_code = tariff_code
    self._last_reset = None
    self._hass = hass

  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return self._is_smart_meter

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_accumulative_consumption"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Previous Accumulative Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.ENERGY

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return ENERGY_KILO_WATT_HOUR

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def last_reset(self):
    """Return the time when the sensor was last reset, if any."""
    return self._last_reset

  @property
  def state(self):
    """Retrieve the previous days accumulative consumption"""
    return self._state
  
  @property
  def should_poll(self) -> bool:
    return True
    
  async def async_update(self):
    await super().async_update()

    if not self.enabled:
      return

    current = now()
    consumption_data = self.coordinator.data["consumption"] if self.coordinator is not None and self.coordinator.data is not None and "consumption" in self.coordinator.data else None
    rate_data = self.coordinator.data["rates"] if self.coordinator is not None and self.coordinator.data is not None and "rates" in self.coordinator.data else None
    standing_charge = self.coordinator.data["standing_charge"] if self.coordinator is not None and self.coordinator.data is not None and "standing_charge" in self.coordinator.data else None

    consumption_and_cost = calculate_electricity_consumption_and_cost(
      current,
      consumption_data,
      rate_data,
      standing_charge,
      self._last_reset,
      self._tariff_code
    )

    if (consumption_and_cost is not None):
      _LOGGER.debug(f"Calculated previous electricity consumption for '{self._mpan}/{self._serial_number}'...")

      await async_import_external_statistics_from_consumption(
        current,
        self._hass,
        get_electricity_consumption_statistic_unique_id(self._serial_number, self._mpan, self._is_export),
        self.name,
        consumption_and_cost["charges"],
        rate_data,
        ENERGY_KILO_WATT_HOUR,
        "consumption"
      )

      self._state = consumption_and_cost["total_consumption"]
      self._last_reset = consumption_and_cost["last_reset"]

      self._attributes = {
        "mpan": self._mpan,
        "serial_number": self._serial_number,
        "is_export": self._is_export,
        "is_smart_meter": self._is_smart_meter,
        "total": consumption_and_cost["total_consumption"],
        "last_calculated_timestamp": consumption_and_cost["last_calculated_timestamp"],
        "charges": list(map(lambda charge: {
          "from": charge["from"],
          "to": charge["to"],
          "consumption": charge["consumption"]
        }, consumption_and_cost["charges"]))
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

        if x == "last_reset":
          self._last_reset = datetime.strptime(state.attributes[x], "%Y-%m-%dT%H:%M:%S%z")

      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeElectricityConsumption state: {self._state}')

  @callback
  async def async_refresh_previous_consumption_data(self, start_date):
    """Update sensors config"""

    await async_refresh_previous_electricity_consumption_data(
      self._hass,
      self._client,
      start_date,
      self._mpan,
      self._serial_number,
      self._tariff_code,
      self._is_smart_meter,
      self._is_export
    )