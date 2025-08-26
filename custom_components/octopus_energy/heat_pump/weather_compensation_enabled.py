import logging

from homeassistant.const import (
    STATE_UNAVAILABLE,
    STATE_UNKNOWN
)
from homeassistant.core import HomeAssistant, callback

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (BaseOctopusEnergyHeatPumpSensor)
from ..utils.attributes import dict_to_typed_dict
from ..api_client.heat_pump import HeatPump
from ..coordinators.heat_pump_configuration_and_status import HeatPumpCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHeatPumpWeatherCompensationEnabled(CoordinatorEntity, BaseOctopusEnergyHeatPumpSensor, BinarySensorEntity, RestoreEntity):
  """Sensor for displaying if weather compensation is enabled for a heat pump."""

  def __init__(self, hass: HomeAssistant, coordinator, heat_pump_id: str, heat_pump: HeatPump):
    """Init sensor."""
    # Pass coordinator to base class
    CoordinatorEntity.__init__(self, coordinator)
    BaseOctopusEnergyHeatPumpSensor.__init__(self, hass, heat_pump_id, heat_pump, "binary_sensor")

    self._state = None
    self._last_updated = None

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_heat_pump_{self._heat_pump_id}_weather_compensation_enabled"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Weather Compensation Enabled Heat Pump ({self._heat_pump_id})"

  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:weather-cloudy"

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    return self._attributes

  @property
  def is_on(self):
    return self._state
  
  @callback
  def _handle_coordinator_update(self) -> None:
    current = now()
    result: HeatPumpCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    
    if (result is not None 
        and result.data is not None 
        and result.data.octoHeatPumpControllerConfiguration is not None
        and result.data.octoHeatPumpControllerConfiguration.heatPump is not None
        and result.data.octoHeatPumpControllerConfiguration.heatPump.weatherCompensation is not None
        and result.data.octoHeatPumpControllerConfiguration.heatPump.weatherCompensation.enabled is not None):
      _LOGGER.debug(f"Updating OctopusEnergyHeatPumpWeatherCompensationEnabled for '{self._heat_pump_id}'")

      self._state = result.data.octoHeatPumpControllerConfiguration.heatPump.weatherCompensation.enabled
      self._last_updated = current

    self._attributes = dict_to_typed_dict(self._attributes)
    super()._handle_coordinator_update()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()

    if state is not None:
      self._state = None if state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN) or state.state is None else state.state.lower() == 'on'
    
    if (self._state is None):
      self._state = False
    
    _LOGGER.debug(f'Restored OctopusEnergyHeatPumpWeatherCompensationEnabled state: {self._state}')