from unittest import mock
import pytest

from homeassistant.exceptions import ServiceValidationError

from custom_components.octopus_energy.const import DOMAIN
from custom_components.octopus_energy.octoplus.event_services import create_octoplus_event_service_handler

class SupportedEntity:
  def __init__(self):
    self.entity_id = "event.octopus_energy_a_12345678_octoplus_power_up_events"
    self._account_id = "A-12345678"
    self.requested_kwargs = None

  async def async_join_weekend_happy_hour_event(self, **kwargs):
    self.requested_kwargs = kwargs
    return { "success": True }

class UnsupportedEntity:
  def __init__(self, account_id):
    self.entity_id = "event.octopus_energy_a_12345678_octoplus_power_down_events"
    if account_id is not None:
      self._account_id = account_id

def create_call():
  call = mock.Mock()
  call.service = "join_octoplus_weekend_happy_hour_event"
  call.data = { "entity_id": ["event.octopus_energy_a_12345678_octoplus_power_up_events"], "event_code": "EVENT_1" }
  return call

@pytest.mark.asyncio
async def test_when_entity_supports_service_then_method_is_called_without_entity_fields():
  # Arrange
  entity = SupportedEntity()
  handler = create_octoplus_event_service_handler("async_join_weekend_happy_hour_event", "octoplus_power_up_events")

  # Act
  result = await handler(entity, create_call())

  # Assert
  assert result == { "success": True }
  assert entity.requested_kwargs == { "event_code": "EVENT_1" }

@pytest.mark.asyncio
@pytest.mark.parametrize("account_id,expected_entity_id", [
  ("A-12345678", "event.octopus_energy_a_12345678_octoplus_power_up_events"),
  (None, "event.octopus_energy_{{ACCOUNT_ID}}_octoplus_power_up_events"),
])
async def test_when_entity_does_not_support_service_then_validation_error_names_expected_entity(account_id, expected_entity_id: str):
  # Arrange
  entity = UnsupportedEntity(account_id)
  handler = create_octoplus_event_service_handler("async_join_weekend_happy_hour_event", "octoplus_power_up_events")

  # Act
  with pytest.raises(ServiceValidationError) as e:
    await handler(entity, create_call())

  # Assert
  assert e.value.translation_domain == DOMAIN
  assert e.value.translation_key == "octoplus_event_service_unsupported_entity"
  assert e.value.translation_placeholders == {
    "entity_id": "event.octopus_energy_a_12345678_octoplus_power_down_events",
    "service": f"{DOMAIN}.join_octoplus_weekend_happy_hour_event",
    "expected_entity_id": expected_entity_id,
  }
