import pytest
from datetime import datetime

from unit import (create_consumption_data, create_rate_data)

from custom_components.octopus_energy.statistics import build_consumption_statistics

@pytest.mark.asyncio
async def test_when_target_rate_specified_then_statistics_restricted():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-28T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  consumptions = create_consumption_data(period_from, period_to, False, "start", "end")
  consumption_key = 'consumption'
  latest_total_sum = 2
  target_rate = 4
  rates = create_rate_data(period_from, period_to, [2, target_rate])

  # Act
  result = build_consumption_statistics(
    current,
    consumptions,
    rates,
    consumption_key,
    latest_total_sum,
    2
  )

  # Assert
  assert result is not None

  expected_sum = latest_total_sum
  expected_state = 0

  for index in range(len(consumptions)):
    item = result[int(index / 2)]

    if index % 2 != 0:
      expected_sum += consumptions[index]["consumption"]
      expected_state += consumptions[index]["consumption"]
      
    expected_start = consumptions[index]["start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state

@pytest.mark.asyncio
async def test_when_target_rate_not_specified_then_statistics_not_restricted():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-28T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  consumptions = create_consumption_data(period_from, period_to, False, "start", "end")
  rates = create_rate_data(period_from, period_to, [2, 4])
  consumption_key = 'consumption'
  latest_total_sum = 3

  # Act
  result = build_consumption_statistics(
    current,
    consumptions,
    rates,
    consumption_key,
    latest_total_sum
  )

  # Assert
  assert result is not None

  expected_sum = latest_total_sum
  expected_state = 0

  for index in range(len(consumptions)):
    item = result[int(index / 2)]
    expected_sum += consumptions[index]["consumption"]
    expected_state += consumptions[index]["consumption"]
    expected_start = consumptions[index]["start"].replace(minute=0, second=0, microsecond=0)

    if index % 2 == 1:
      assert "start" in item
      assert item["start"] == expected_start

      assert "last_reset" in item
      assert item["last_reset"] == consumptions[0]["start"]

      assert "sum" in item
      assert item["sum"] == expected_sum

      assert "state" in item
      assert item["state"] == expected_state