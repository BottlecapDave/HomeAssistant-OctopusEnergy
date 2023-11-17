from datetime import (datetime)
import pytest

from unit import (create_rate_data)
from custom_components.octopus_energy.utils.rate_information import get_next_rate_information
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
from .. import agile_rates

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_gmt_then_no_rate_information_is_returned():
  # Arrange
  now = datetime.strptime("2022-03-01T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = agile_rates

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_no_rates_and_bst_then_no_rate_information_is_returned():
  # Arrange
  now = datetime.strptime("2022-03-02T00:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = agile_rates

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_is_at_start_of_rates_and_bst_then_no_rate_information_is_returned():
  # Arrange
  now = datetime.strptime("2022-10-20T23:59:59+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = agile_rates

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_next_rate_is_identical_to_current_rate_then_no_rate_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-02-28T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T00:12:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = create_rate_data(period_from, period_to, [10])

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is None

@pytest.mark.asyncio
async def test_when_target_has_rates_and_gmt_then_rate_information_is_returned():
  # Arrange
  now = datetime.strptime("2022-10-21T03:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = agile_rates
  expected_current_rate = 21.21

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "next_rate" in rate_information
  assert rate_information["next_rate"]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["next_rate"]["start"] == datetime.strptime("2022-10-21T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["next_rate"]["end"] == datetime.strptime("2022-10-21T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert "applicable_rates" in rate_information
  assert len(rate_information["applicable_rates"]) == 2

  assert rate_information["applicable_rates"][0]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][0]["start"] == datetime.strptime("2022-10-21T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][0]["end"] == datetime.strptime("2022-10-21T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert rate_information["applicable_rates"][1]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][1]["start"] == datetime.strptime("2022-10-21T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][1]["end"] == datetime.strptime("2022-10-21T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_target_has_rates_and_bst_then_rate_information_is_returned():
  # Arrange
  now = datetime.strptime("2022-10-21T04:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = agile_rates
  expected_current_rate = 21.21

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "next_rate" in rate_information
  assert rate_information["next_rate"]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["next_rate"]["start"] == datetime.strptime("2022-10-21T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["next_rate"]["end"] == datetime.strptime("2022-10-21T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert "applicable_rates" in rate_information
  assert len(rate_information["applicable_rates"]) == 2

  assert rate_information["applicable_rates"][0]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][0]["start"] == datetime.strptime("2022-10-21T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][0]["end"] == datetime.strptime("2022-10-21T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert rate_information["applicable_rates"][1]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][1]["start"] == datetime.strptime("2022-10-21T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][1]["end"] == datetime.strptime("2022-10-21T04:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

@pytest.mark.asyncio
async def test_when_all_rates_different_then_rate_information_is_returned():
  # Arrange
  now = datetime.strptime("2022-10-21T05:30:00+01:00", "%Y-%m-%dT%H:%M:%S%z")

  rate_data = agile_rates
  expected_current_rate = 22.449

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "next_rate" in rate_information
  assert rate_information["next_rate"]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["next_rate"]["start"] == datetime.strptime("2022-10-21T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["next_rate"]["end"] == datetime.strptime("2022-10-21T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert "applicable_rates" in rate_information
  assert len(rate_information["applicable_rates"]) == 1

  assert rate_information["applicable_rates"][0]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][0]["start"] == datetime.strptime("2022-10-21T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][0]["end"] == datetime.strptime("2022-10-21T05:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

# Covering https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/issues/441
@pytest.mark.asyncio
@pytest.mark.parametrize("now",[
  (datetime.strptime("2023-10-06T10:50:00+01:00", "%Y-%m-%dT%H:%M:%S%z")),
  (datetime.strptime("2023-10-06T09:50:00Z", "%Y-%m-%dT%H:%M:%S%z")),
])
async def test_when_agile_rates_then_rate_information_is_returned(now: datetime):
  # Arrange
  rate_data = rates_to_thirty_minute_increments(
    {
      "results": [
        {
          "value_inc_vat": 2.0,
          "valid_from": "2023-10-06T11:30:00Z",
          "valid_to": "2023-10-06T12:00:00Z"
        },
        {
          "value_inc_vat": 3.02,
          "valid_from": "2023-10-06T11:00:00Z",
          "valid_to": "2023-10-06T11:30:00Z"
        },
        {
          "value_inc_vat": 3.43,
          "valid_from": "2023-10-06T10:30:00Z",
          "valid_to": "2023-10-06T11:00:00Z"
        },
        {
          "value_inc_vat": 4.18,
          "valid_from": "2023-10-06T10:00:00Z",
          "valid_to": "2023-10-06T10:30:00Z"
        },
        {
          "value_inc_vat": 6.19,
          "valid_from": "2023-10-06T09:30:00Z",
          "valid_to": "2023-10-06T10:00:00Z"
        },
        {
          "value_inc_vat": 6.74,
          "valid_from": "2023-10-06T09:00:00Z",
          "valid_to": "2023-10-06T09:30:00Z"
        },
        {
          "value_inc_vat": 7.6,
          "valid_from": "2023-10-06T08:30:00Z",
          "valid_to": "2023-10-06T09:00:00Z"
        },
      ]
    },
    datetime.strptime("2023-10-06T09:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    datetime.strptime("2023-10-06T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z"),
    "test"
  )
  expected_current_rate = 4.18

  # Act
  rate_information = get_next_rate_information(rate_data, now)

  # Assert
  assert rate_information is not None
  
  assert "next_rate" in rate_information
  assert rate_information["next_rate"]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["next_rate"]["start"] == datetime.strptime("2023-10-06T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["next_rate"]["end"] == datetime.strptime("2023-10-06T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z")

  assert "applicable_rates" in rate_information
  assert len(rate_information["applicable_rates"]) == 1

  assert rate_information["applicable_rates"][0]["value_inc_vat"] == round(expected_current_rate / 100, 6)
  assert rate_information["applicable_rates"][0]["start"] == datetime.strptime("2023-10-06T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert rate_information["applicable_rates"][0]["end"] == datetime.strptime("2023-10-06T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
