from homeassistant.core import callback

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)

from ..utils.error import exception_to_string
from ..coordinators.intelligent_dispatches import IntelligentDispatchesCoordinatorResult
from .base import OctopusEnergyBaseDataLastRetrieved

class OctopusEnergyIntelligentDispatchesDataLastRetrieved(OctopusEnergyBaseDataLastRetrieved):
  """Sensor for displaying the last time the intelligent dispatches data was last retrieved."""

  def __init__(self, hass, coordinator, account_id):
    """Init sensor."""
    self._account_id = account_id
    OctopusEnergyBaseDataLastRetrieved.__init__(self, hass, coordinator)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_intelligent_dispatches_data_last_retrieved"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Intelligent Dispatches Data Last Retrieved ({self._account_id})"
  
  @callback
  def _handle_coordinator_update(self) -> None:
    result: IntelligentDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    self._state = result.last_retrieved if result is not None else None

    self._attributes = {
      "attempts": result.request_attempts if result is not None else None,
      "next_refresh": result.next_refresh if result is not None else None,
      "last_error": exception_to_string(result.last_error) if result is not None else None,
      "requests_current_hour": result.requests_current_hour if result is not None else None,
      "request_limits_last_reset": result.requests_current_hour_last_reset if result is not None else None
    }

    CoordinatorEntity._handle_coordinator_update(self)