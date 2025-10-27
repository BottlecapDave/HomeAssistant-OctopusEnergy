from datetime import datetime
import logging

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.util.dt import (utcnow)

from homeassistant.helpers.update_coordinator import (
  CoordinatorEntity
)
from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
)
from homeassistant.helpers.restore_state import RestoreEntity

from . import (
  get_current_and_next_forecast
)

from .base import OctopusEnergyGreennessForecastSensor
from ..coordinators.greenness_forecast import GreennessForecastCoordinatorResult
from ..api_client.greenness_forecast import GreennessForecast

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyGreenerNightsSessionsCalendar(OctopusEnergyGreennessForecastSensor, CoordinatorEntity, CalendarEntity, RestoreEntity):
  """Sensor for determining the greener nights."""
  
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    """Init sensor."""

    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyGreennessForecastSensor.__init__(self, account_id)
  
    self._account_id = account_id
    self._event = None
    self._extra_attributes = {}
    self._events = []

    self.entity_id = generate_entity_id("calendar.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_greener_nights"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Greener Nights ({self._account_id})"
  
  @property
  def event(self) -> CalendarEvent | None:
    """Return the next upcoming event."""
    return self._event
  
  def _greenness_forecast_to_calendar_event(self, forecast: GreennessForecast) -> CalendarEvent:
    """Convert a greenness forecast to a calendar event."""
    return CalendarEvent(
      uid=forecast.start.isoformat(),
      summary="Octopus Energy Greener Night",
      start=forecast.start,
      end=forecast.end,
      description=f"Score: {forecast.greenness_score}\nIndex: {forecast.greenness_index}"
    )
  
  @callback
  def _handle_coordinator_update(self) -> None:
    """Determine if the user is in a free electricity session."""

    result: GreennessForecastCoordinatorResult = self.coordinator.data if self.coordinator is not None and self.coordinator.data is not None else None
    forecast = result.forecast if result is not None else None
    if (forecast is not None):
      self._events = forecast
    else:
      self._events = []

    current_date = utcnow()
    current_and_next = get_current_and_next_forecast(current_date, forecast, True)
    self._event = None
    self._extra_attributes = {}
    if (current_and_next is not None):
      if (current_and_next.current is not None):
        self._event = self._greenness_forecast_to_calendar_event(current_and_next.current)
        self._extra_attributes = {
          "greenness_index": current_and_next.current.greenness_index,
          "greenness_score": current_and_next.current.greenness_score,
        }
      elif (current_and_next.next is not None):
        self._event = self._greenness_forecast_to_calendar_event(current_and_next.next)
        self._extra_attributes = {
          "greenness_index": current_and_next.next.greenness_index,
          "greenness_score": current_and_next.next.greenness_score,
        }

    super()._handle_coordinator_update()

  async def async_get_events(
    self, hass, start_date: datetime, end_date: datetime
  ) -> list[CalendarEvent]:
    """Get all events in a specific time frame."""
    events = []
    if self._events is not None:
      for event in self._events:
        if event.start < end_date and event.end > start_date and event.highlight_flag:
          events.append(self._greenness_forecast_to_calendar_event(event))

    return events
  
  @property
  def extra_state_attributes(self):
    """Return the device state attributes."""
    return self._extra_attributes
