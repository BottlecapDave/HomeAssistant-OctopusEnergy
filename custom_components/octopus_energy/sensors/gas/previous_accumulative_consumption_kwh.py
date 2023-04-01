import logging
from datetime import datetime

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.const import (
    ENERGY_KILO_WATT_HOUR
)

from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_import_statistics
)

from .. import (
  calculate_gas_consumption,
)

from .base import (OctopusEnergyGasSensor)

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeGasConsumptionKwh(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the previous days accumulative gas consumption in kwh."""

  def __init__(self, hass, coordinator, mprn, serial_number, native_consumption_units, calorific_value):
    """Init sensor."""
    super().__init__(coordinator)
    OctopusEnergyGasSensor.__init__(self, mprn, serial_number)

    self._hass = hass
    self._native_consumption_units = native_consumption_units
    self._state = None
    self._latest_date = None
    self._calorific_value = calorific_value

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_consumption_kwh"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Previous Accumulative Consumption (kWh)"

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
    return "mdi:fire"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def last_reset(self):
    """Return the time when the sensor was last reset, if any."""
    return self._latest_date

  @property
  def state(self):
    """Retrieve the previous days accumulative consumption"""
    return self._state
  
  @property
  def should_poll(self) -> bool:
    return True
    
  async def async_update(self):
    consumption = calculate_gas_consumption(
      self.coordinator.data,
      self._latest_date,
      self._native_consumption_units,
      self._calorific_value
    )

    if (consumption != None):
      _LOGGER.debug(f"Calculated previous gas consumption for '{self._mprn}/{self._serial_number}'...")

      if self._latest_date is not None and self._latest_date != consumption["last_calculated_timestamp"] and consumption["consumptions"] is not None:
        statistic_id = f"sensor.{self.unique_id}".lower()
        statistics = []
        
        last_reset = consumption["consumptions"][0]["from"].replace(minute=0, second=0, microsecond=0)
        current_start = last_reset
        sum = 0
        
        for charge in consumption["consumptions"]:
          start = charge["from"].replace(minute=0, second=0, microsecond=0)
          if current_start == start:
            sum += charge["consumption_kwh"]
          else:
            statistics.append(
              StatisticData(
                  start=start,
                  last_reset=last_reset,
                  state=sum,
                  sum=statistics[-1]["sum"] - sum if len(statistics) > 0 else sum
              )
            )
            current_start = start
            sum = charge["consumption_kwh"]

        metadata = StatisticMetaData(
          has_mean=False,
          has_sum=True,
          name=self.name,
          source='recorder',
          statistic_id=statistic_id,
          unit_of_measurement=ENERGY_KILO_WATT_HOUR,
        )

        async_import_statistics(self._hass, metadata, statistics)
        _LOGGER.debug(f"Imported statistics for '{self._mprn}/{self._serial_number}'...")

      self._state = consumption["total_kwh"]
      self._latest_date = consumption["last_calculated_timestamp"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "is_estimated": self._native_consumption_units == "m³",
        "last_calculated_timestamp": consumption["last_calculated_timestamp"],
        "charges": consumption["consumptions"],
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

        if x == "last_reset":
          self._latest_date = datetime.strptime(state.attributes[x], "%Y-%m-%dT%H:%M:%S%z")
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasConsumptionKwh state: {self._state}')