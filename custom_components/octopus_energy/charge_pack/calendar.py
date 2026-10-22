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

from . import calendar_dispatches, current_or_next_dispatch, kind_to_friendly_string
from .base import OctopusEnergyChargePackSensor
from ..api_client.charge_pack import ChargePackDevice, ChargePackDispatch
from ..coordinators.charge_pack import ChargePackDispatchesCoordinatorResult

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyChargePackCalendar(CoordinatorEntity, OctopusEnergyChargePackSensor, CalendarEntity):
  """The Charge Pack's planned charges (or discharges), and the ones that have happened."""

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str, device: ChargePackDevice, kind: str):
    """Init sensor."""
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyChargePackSensor.__init__(self, device)

    self._account_id = account_id
    self._kind = kind
    self._event = None
    self._dispatches: list[ChargePackDispatch] = []

    self.entity_id = generate_entity_id("calendar.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_{self._device.id}_charge_pack_{self._kind}"

  @property
  def name(self):
    """Name of the sensor."""
    return f"Charge Pack {kind_to_friendly_string(self._kind)} ({self._account_id})"

  @property
  def icon(self):
    return "mdi:battery-arrow-up" if self._kind == "charge" else "mdi:battery-arrow-down"

  async def async_added_to_hass(self) -> None:
    """Read the plan straight away, rather than at the coordinator's next minute."""
    await super().async_added_to_hass()
    if self.coordinator.data is not None:
      self._handle_coordinator_update()
    else:
      await self.coordinator.async_request_refresh()

  @property
  def event(self) -> CalendarEvent | None:
    """The event running now, or the next one."""
    return self._event

  def _to_event(self, dispatch: ChargePackDispatch) -> CalendarEvent:
    return CalendarEvent(
      uid=f"{self._device.id}_{self._kind}_{dispatch.start.isoformat()}",
      summary=f"{kind_to_friendly_string(self._kind)} {dispatch.kwh:.2f} kWh",
      start=dispatch.start,
      end=dispatch.end,
      description=f"Planned by Octopus Energy for {self._device.name or 'your home battery'}" + (f" ({dispatch.type})" if dispatch.type else ""),
    )

  @callback
  def _handle_coordinator_update(self) -> None:
    result: ChargePackDispatchesCoordinatorResult = self.coordinator.data if self.coordinator is not None else None
    self._dispatches = calendar_dispatches(result.history, result.planned, self._kind) if result is not None else []
    found = current_or_next_dispatch(self._dispatches, utcnow())
    self._event = self._to_event(found) if found is not None else None
    self._attributes = {"data_last_retrieved": result.last_retrieved if result is not None else None}
    super()._handle_coordinator_update()

  @property
  def extra_state_attributes(self):
    return getattr(self, "_attributes", {})

  async def async_get_events(self, hass, start_date: datetime, end_date: datetime) -> list[CalendarEvent]:
    """The events in a time frame."""
    return [self._to_event(d) for d in self._dispatches if d.start < end_date and d.end > start_date]
