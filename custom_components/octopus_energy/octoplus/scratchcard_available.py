from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import is_scratchcard_available
from .base import OctopusEnergyOctoplusSensor


class OctopusEnergyOctoplusScratchcardAvailable(CoordinatorEntity, OctopusEnergyOctoplusSensor, BinarySensorEntity):
  """Sensor indicating whether an Octoplus scratchcard is available to scratch."""

  def __init__(self, hass: HomeAssistant, coordinator, account_id: str):
    CoordinatorEntity.__init__(self, coordinator)
    OctopusEnergyOctoplusSensor.__init__(self, account_id)
    self._account_id = account_id
    self.entity_id = generate_entity_id("binary_sensor.{}", self.unique_id, hass=hass)

  @property
  def unique_id(self):
    return f"octopus_energy_{self._account_id}_octoplus_scratchcard_available"

  @property
  def name(self):
    return f"Octoplus Scratchcard Available ({self._account_id})"

  @property
  def icon(self):
    return "mdi:ticket"

  @property
  def available(self):
    return super().available and self.coordinator.data is not None

  @property
  def is_on(self):
    result = self.coordinator.data
    return is_scratchcard_available(result.data if result is not None else None)

  @property
  def extra_state_attributes(self):
    result = self.coordinator.data
    if result is None or result.data is None:
      return {}

    data = result.data.model_dump()
    session = data["activeSession"] or {}
    scratchcard = data["scratchcard"] or {}
    offer = scratchcard.get("offer") or {}
    prize = scratchcard.get("prize") or {}
    return {
      "starts_at": session.get("startsAt"),
      "ends_at": session.get("endsAt"),
      "session_external_reference": session.get("externalReference"),
      "scratchcard_external_reference": scratchcard.get("externalReference"),
      "scratchcard_status": scratchcard.get("status"),
      "offer_slug": offer.get("slug"),
      "feature_display_text": offer.get("featureDisplayText"),
      "prize_type": prize.get("typename"),
    }
