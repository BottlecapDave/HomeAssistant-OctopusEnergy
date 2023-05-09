import pytest
from datetime import datetime

from unit import (create_consumption_data, create_rate_data)

from custom_components.octopus_energy.statistics import build_consumption_statistics

@pytest.mark.asyncio
async def test_when_two_rates_available_then_total_peak_and_off_peak_available():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumptions = create_consumption_data(period_from, period_to)
  rates = create_rate_data(period_from, period_to, [2, 4])
  consumption_key = 'consumption'
  latest_total_sum = 3
  latest_peak_sum = 2
  latest_off_peak_sum = 1

  # Act
  result = build_consumption_statistics(
    consumptions,
    rates,
    consumption_key,
    latest_total_sum,
    latest_peak_sum,
    latest_off_peak_sum
  )

  # Assert
  assert result is not None

  expected_sum = latest_total_sum
  expected_state = 0

  assert "total" in result
  for index in range(len(consumptions)):
    item = result["total"][int(index / 2)]
    expected_sum += consumptions[index]["consumption"]
    expected_state += consumptions[index]["consumption"]
    expected_start = consumptions[index]["interval_start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["interval_start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state

  expected_sum = latest_off_peak_sum
  expected_state = 0

  assert "off_peak" in result
  for index in range(len(consumptions)):
    item = result["off_peak"][int(index / 2)]

    if index % 2 == 0:
      expected_sum += consumptions[index]["consumption"]
      expected_state += consumptions[index]["consumption"]
      
    expected_start = consumptions[index]["interval_start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["interval_start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state

  expected_sum = latest_peak_sum
  expected_state = 0

  assert "peak" in result
  for index in range(len(consumptions)):
    item = result["peak"][int(index / 2)]

    if index % 2 != 0:
      expected_sum += consumptions[index]["consumption"]
      expected_state += consumptions[index]["consumption"]
      
    expected_start = consumptions[index]["interval_start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["interval_start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state

@pytest.mark.asyncio
@pytest.mark.parametrize("expected_rates",[
  ([2]),
  ([2, 4, 6])
])
async def test_when_more_or_less_than_two_rates_available_then_off_peak_not_available(expected_rates):
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  consumptions = create_consumption_data(period_from, period_to)
  rates = create_rate_data(period_from, period_to, expected_rates)
  consumption_key = 'consumption'
  latest_total_sum = 3
  latest_peak_sum = 2
  latest_off_peak_sum = 0

  # Act
  result = build_consumption_statistics(
    consumptions,
    rates,
    consumption_key,
    latest_total_sum,
    latest_peak_sum,
    latest_off_peak_sum
  )

  # Assert
  assert result is not None

  expected_sum = latest_total_sum
  expected_state = 0

  assert "total" in result
  for index in range(len(consumptions)):
    item = result["total"][int(index / 2)]
    expected_sum += consumptions[index]["consumption"]
    expected_state += consumptions[index]["consumption"]
    expected_start = consumptions[index]["interval_start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["interval_start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state

  assert "off_peak" in result
  for index in range(len(consumptions)):
    item = result["off_peak"][int(index / 2)]
    expected_start = consumptions[index]["interval_start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["interval_start"]

      assert "sum" in item
      assert item["sum"] == 0

      assert "state" in item
      assert item["state"] == 0

  expected_sum = latest_peak_sum
  expected_state = 0

  assert "peak" in result
  for index in range(len(consumptions)):
    item = result["peak"][int(index / 2)]

    expected_sum += consumptions[index]["consumption"]
    expected_state += consumptions[index]["consumption"]
      
    expected_start = consumptions[index]["interval_start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["interval_start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state