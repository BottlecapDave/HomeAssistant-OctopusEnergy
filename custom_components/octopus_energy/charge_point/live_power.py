import asyncio
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.const import UnitOfPower
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.sensor import (
  SensorEntity,
  SensorDeviceClass,
  SensorStateClass,
)

from .base import (BaseOctopusEnergyChargePointSensor)
from ..api_client import OctopusEnergyApiClient
from ..api_client.charge_point import OnboardedChargePoint
from ..coordinators.charge_point_configuration_and_status import ChargePointCoordinatorResult

_LOGGER = logging.getLogger(__name__)

charging_states = ["CHARGING", "BOOST_CHARGING"]

# Reconnect backoff while the charge point is still reporting a charging
# state but the stream itself has dropped
initial_reconnect_delay_seconds = 5
max_reconnect_delay_seconds = 60

class OctopusEnergyChargePointLivePower(CoordinatorEntity, BaseOctopusEnergyChargePointSensor, SensorEntity):
  """Sensor for displaying the live power draw of a charge point.

  Unlike every other sensor in this integration, this one is push-driven
  rather than polling-coordinator-driven: it starts/stops a background
  streaming task based on the polling coordinator's operationalState, and
  each reading calls async_write_ha_state() directly, bypassing the
  coordinator. Deliberately not a RestoreSensor - a stale "last known kW"
  value surviving a HA restart would be misleading for something this
  transient.
  """

  def __init__(self, hass: HomeAssistant, coordinator, client: OctopusEnergyApiClient, account_id: str, charge_point_id: str, charge_point: OnboardedChargePoint, is_mocked: bool):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyChargePointSensor.__init__(self, hass, charge_point_id, charge_point)

    self._client = client
    self._account_id = account_id
    self._is_mocked = is_mocked
    # 0kW rather than unknown/None - not charging genuinely means no power is
    # being drawn, which is a real, known value, not an absence of data.
    self._state = 0
    self._stream_task: asyncio.Task | None = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_charge_point_{self._charge_point_id}_live_power"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Live Power Charge Point ({self._charge_point_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:lightning-bolt"

  @property
  def device_class(self):
    """The type of sensor"""
    return SensorDeviceClass.POWER

  @property
  def native_unit_of_measurement(self):
    """The unit of measurement of sensor"""
    return UnitOfPower.KILO_WATT

  @property
  def state_class(self):
    """The state class of sensor"""
    return SensorStateClass.MEASUREMENT

  @property
  def native_value(self):
    return self._state

  @callback
  def _handle_coordinator_update(self) -> None:
    """Start/stop the live power stream based on the charge point's operational state."""
    result: ChargePointCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    operational_state = result.data.operationalState if result is not None and result.data is not None else None

    is_charging = operational_state in charging_states

    if is_charging and (self._stream_task is None or self._stream_task.done()):
      if self._is_mocked:
        # Mock mode has no real multipart stream to connect to - leave the
        # sensor unavailable rather than fabricate readings.
        _LOGGER.debug(f"Skipping live power stream for mocked charge point '{self._charge_point_id}'")
      elif self.hass is not None:
        _LOGGER.debug(f"Starting live power stream for charge point '{self._charge_point_id}'")
        self._stream_task = self.hass.async_create_task(self._async_stream_power())
    elif not is_charging and self._stream_task is not None and not self._stream_task.done():
      _LOGGER.debug(f"Stopping live power stream for charge point '{self._charge_point_id}' - no longer charging")
      self._stream_task.cancel()
      self._stream_task = None
      self._state = 0
      self.async_write_ha_state()

    super()._handle_coordinator_update()

  async def _async_stream_power(self):
    """Consume the live power stream, reconnecting with backoff on a dropped connection while still charging."""
    reconnect_delay = initial_reconnect_delay_seconds
    try:
      while True:
        try:
          async for reading in self._client.async_stream_charge_point_power(self._account_id, self._charge_point_id):
            reconnect_delay = initial_reconnect_delay_seconds

            if reading is not None and "value" in reading:
              self._state = float(reading["value"])
            else:
              # Stream reported no reading (e.g. charging just stopped) - 0kW
              # is the accurate value here, not unknown.
              self._state = 0

            self.async_write_ha_state()

          # Stream ended cleanly - nothing more to read, so stop
          return
        except asyncio.CancelledError:
          raise
        except Exception as e:
          _LOGGER.debug(f"Live power stream for charge point '{self._charge_point_id}' dropped: {e}. Reconnecting in {reconnect_delay}s")
          await asyncio.sleep(reconnect_delay)
          reconnect_delay = min(reconnect_delay * 2, max_reconnect_delay_seconds)
    except asyncio.CancelledError:
      _LOGGER.debug(f"Live power stream for charge point '{self._charge_point_id}' cancelled")
      raise

  async def async_will_remove_from_hass(self) -> None:
    """Ensure the streaming connection is cleaned up when the entity is removed."""
    if self._stream_task is not None and not self._stream_task.done():
      self._stream_task.cancel()
      self._stream_task = None

    await super().async_will_remove_from_hass()
