from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.util.dt import parse_datetime

from custom_components.octopus_energy.api_client.octoplus import OctoplusScratchcardResponse
from custom_components.octopus_energy.binary_sensor import async_setup_entry
from custom_components.octopus_energy.const import CONFIG_ACCOUNT_ID, CONFIG_KIND, CONFIG_KIND_ACCOUNT, DATA_ACCOUNT, DOMAIN
from custom_components.octopus_energy.octoplus import is_scratchcard_available
from custom_components.octopus_energy.octoplus.scratchcard_available import OctopusEnergyOctoplusScratchcardAvailable


session = {
  "startsAt": "2026-09-27T23:00:00+00:00",
  "endsAt": "2026-09-28T23:00:00+00:00",
  "externalReference": "session-reference",
}
scratchcard = {
  "externalReference": "scratchcard-reference",
  "status": "PRIZE_CLAIMED",
  "offer": {
    "slug": "caffe-nero-coffee-scratchcard",
    "featureDisplayText": "a free hot or cold drink from Caffé Nero",
  },
  "prize": {"__typename": "OctoplusOfferType"},
}


@pytest.mark.parametrize("active_session,card,expected", [
  (None, None, False),
  (session, None, True),
  (session, scratchcard, False),
  (None, scratchcard, False),
  ({}, None, True),
  (session, {}, False),
])
def test_scratchcard_availability(active_session, card, expected):
  data = OctoplusScratchcardResponse.model_validate({
    "activeSession": active_session,
    "scratchcard": card,
  })
  assert is_scratchcard_available(data) is expected


def test_when_data_missing_then_scratchcard_not_available():
  assert is_scratchcard_available(None) is False


@pytest.mark.asyncio
@pytest.mark.parametrize("active_session,card", [
  (None, None),
  ({}, {}),
  ({}, {"offer": None, "prize": None}),
  ({}, {"offer": {}, "prize": {}}),
])
async def test_when_optional_fields_missing_then_attributes_are_none(active_session, card):
  data = OctoplusScratchcardResponse.model_validate({
    "activeSession": active_session,
    "scratchcard": card,
  })
  coordinator = Mock(data=SimpleNamespace(data=data))
  sensor = OctopusEnergyOctoplusScratchcardAvailable(HomeAssistant("/tmp"), coordinator, "A-12345678")
  assert sensor.extra_state_attributes == {
    "starts_at": None,
    "ends_at": None,
    "session_external_reference": None,
    "scratchcard_external_reference": None,
    "scratchcard_status": None,
    "offer_slug": None,
    "feature_display_text": None,
    "prize_type": None,
  }


@pytest.mark.asyncio
async def test_sensor_state_and_attributes_follow_coordinator():
  hass = HomeAssistant("/tmp")
  coordinator = Mock()
  coordinator.last_update_success = True
  coordinator.data = SimpleNamespace(data=OctoplusScratchcardResponse.model_validate({
    "activeSession": session,
    "scratchcard": None,
  }))
  sensor = OctopusEnergyOctoplusScratchcardAvailable(hass, coordinator, "A-12345678")

  assert sensor.entity_id == "binary_sensor.octopus_energy_a_12345678_octoplus_scratchcard_available"
  assert sensor.unique_id == "octopus_energy_A-12345678_octoplus_scratchcard_available"
  assert sensor.device_info["identifiers"] == {(DOMAIN, "octoplus-A-12345678")}
  assert sensor.available is True
  assert sensor.is_on is True
  assert sensor.extra_state_attributes["starts_at"] == parse_datetime(session["startsAt"])
  assert sensor.extra_state_attributes["ends_at"] == parse_datetime(session["endsAt"])
  assert sensor.extra_state_attributes["session_external_reference"] == "session-reference"
  assert sensor.extra_state_attributes["scratchcard_status"] is None

  coordinator.data = SimpleNamespace(data=OctoplusScratchcardResponse.model_validate({
    "activeSession": session,
    "scratchcard": scratchcard,
  }))
  assert sensor.is_on is False
  assert sensor.extra_state_attributes == {
    "starts_at": parse_datetime(session["startsAt"]),
    "ends_at": parse_datetime(session["endsAt"]),
    "session_external_reference": "session-reference",
    "scratchcard_external_reference": "scratchcard-reference",
    "scratchcard_status": "PRIZE_CLAIMED",
    "offer_slug": "caffe-nero-coffee-scratchcard",
    "feature_display_text": "a free hot or cold drink from Caffé Nero",
    "prize_type": "OctoplusOfferType",
  }

  coordinator.data = SimpleNamespace(data=OctoplusScratchcardResponse.model_validate({
    "activeSession": None,
    "scratchcard": None,
  }))
  assert sensor.is_on is False
  assert sensor.available is True
  assert all(value is None for value in sensor.extra_state_attributes.values())

  coordinator.data = SimpleNamespace(data=None)
  assert sensor.available is True
  assert sensor.extra_state_attributes == {}
  coordinator.data = None
  assert sensor.available is False
  assert sensor.is_on is False


@pytest.mark.asyncio
@pytest.mark.parametrize("enrolled", [True, False])
async def test_account_setup_only_adds_scratchcard_sensor_when_enrolled(enrolled):
  hass = HomeAssistant("/tmp")
  account_id = "A-12345678"
  hass.data[DOMAIN] = {account_id: {
    DATA_ACCOUNT: SimpleNamespace(account={
      "electricity_meter_points": [],
      "octoplus_enrolled": enrolled,
    }),
  }}
  entry = SimpleNamespace(data={CONFIG_KIND: CONFIG_KIND_ACCOUNT, CONFIG_ACCOUNT_ID: account_id})
  coordinator = Mock(async_refresh=AsyncMock())
  add_entities = Mock()
  with patch("custom_components.octopus_energy.binary_sensor.async_setup_octoplus_scratchcard_coordinator", AsyncMock(return_value=coordinator)) as setup:
    with patch("custom_components.octopus_energy.binary_sensor.async_get_account_debug_override", AsyncMock(return_value=None)):
      await async_setup_entry(hass, entry, add_entities)

  if enrolled:
    setup.assert_awaited_once_with(hass, account_id)
    coordinator.async_refresh.assert_awaited_once()
    assert len(add_entities.call_args.args[0]) == 1
    assert isinstance(add_entities.call_args.args[0][0], OctopusEnergyOctoplusScratchcardAvailable)
  else:
    setup.assert_not_awaited()
    add_entities.assert_not_called()


@pytest.mark.asyncio
async def test_non_account_entry_does_not_add_scratchcard_sensor():
  add_entities = Mock()
  await async_setup_entry(HomeAssistant("/tmp"), SimpleNamespace(data={CONFIG_KIND: "target_rate"}), add_entities)
  add_entities.assert_not_called()
