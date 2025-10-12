from homeassistant.core import callback

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)

from ..utils.error import exception_to_string
from ..coordinators.intelligent_dispatches import MAXIMUM_DISPATCH_REQUESTS_PER_HOUR, IntelligentDispatchesCoordinatorResult
from .base import OctopusEnergyBaseDataLastRetrieved
from ..intelligent.base import OctopusEnergyIntelligentSensor
from ..api_client.intelligent_device import IntelligentDevice

class OctopusEnergyIntelligentDispatchesDataLastRetrieved(OctopusEnergyIntelligentSensor, OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the intelligent dispatches data was last retrieved."""

  def __init__(self, hass, coordinator, account_id: str, device: IntelligentDevice):
    """Init sensor."""
    self._account_id = account_id
    self._device_id = device.id
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)
    OctopusEnergyIntelligentSensor.__init__(self, device)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._device_id}_intelligent_dispatches_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Dispatches Data Last Retrieved ({self._device_id})"
  
  @callback
  def _handle_coordinator_update(self) -> None:
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    self._state = result.last_retrieved if result is not None else None

    self._attributes = {
      "attempts": result.request_attempts if result is not None else None,
      "next_refresh": result.next_refresh if result is not None else None,
      "last_error": exception_to_string(result.last_error) if result is not None else None,
      "requests_current_hour": result.requests_current_hour if result is not None else None,
      "maximum_requests_per_hour": MAXIMUM_DISPATCH_REQUESTS_PER_HOUR,
      "request_limits_last_reset": result.requests_current_hour_last_reset if result is not None else None
    }

    CoordinatorEntity._handle_coordinator_update(self)