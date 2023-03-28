import logging
from datetime import (timedelta)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass
)
from homeassistant.const import (
    VOLUME_CUBIC_METERS
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

class OctopusEnergyPreviousAccumulativeGasConsumption(CoordinatorEntity, OctopusEnergyGasSensor):
  """Sensor for displaying the previous days accumulative gas reading."""

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
    return f"octopus_energy_gas_{self._serial_number}_{self._mprn}_previous_accumulative_consumption"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Gas {self._serial_number} {self._mprn} Previous Accumulative Consumption"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.GAS

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.TOTAL

  @property
  def unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return VOLUME_CUBIC_METERS

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
        sum = 0
        for charge in consumption["consumptions"]:
          sum += charge["consumption_m3"]
          start = charge["from"].replace(minute=0, second=0, microsecond=0)
          
          statistics.append(
             StatisticData(
                start=start,
                sum=sum
            )
          )

        metadata = StatisticMetaData(
          has_mean=False,
          has_sum=True,
          name=self.name,
          source='recorder',
          statistic_id=statistic_id,
          unit_of_measurement=VOLUME_CUBIC_METERS,
        )

        async_import_statistics(self._hass, metadata, statistics)
        _LOGGER.debug(f"Imported statistics for '{self._mprn}/{self._serial_number}'...")

      self._state = consumption["total_m3"]
      self._latest_date = consumption["last_calculated_timestamp"]

      self._attributes = {
        "mprn": self._mprn,
        "serial_number": self._serial_number,
        "is_estimated": self._native_consumption_units != "m³",
        "total_kwh": consumption["total_kwh"],
        "total_m3": consumption["total_m3"],
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
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeGasConsumption state: {self._state}')