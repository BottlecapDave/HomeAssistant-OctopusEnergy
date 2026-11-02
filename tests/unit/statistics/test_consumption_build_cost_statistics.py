import pytest
from datetime import datetime, timedelta

from unit import (create_consumption_data, create_rate_data)

from custom_components.octopus_energy.statistics import build_cost_statistics
from custom_components.octopus_energy.utils.conversions import consumption_cost_in_pence

@pytest.mark.asyncio
async def test_when_target_rate_specified_then_statistics_restructed():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-28T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  consumptions = create_consumption_data(period_from, period_to, False, "start", "end")
  consumption_key = 'consumption'
  latest_total_sum = 3
  target_rate = 4
  rates = create_rate_data(period_from, period_to, [2, target_rate])

  # Act
  result = build_cost_statistics(
    current,
    consumptions,
    rates,
    consumption_key,
    latest_total_sum,
    target_rate=target_rate
  )

  # Assert
  assert result is not None

  expected_sum = latest_total_sum
  expected_state = 0

  for index in range(len(consumptions)):
    if index % 2 != 0:
      expected_sum += round((consumptions[index]["consumption"] * rates[index]["value_inc_vat"]) / 100, 2)
      expected_state += round((consumptions[index]["consumption"] * rates[index]["value_inc_vat"]) / 100, 2)
      
    if index % 2 == 1:
      expected_start = consumptions[index]["start"].replace(minute=0, second=0, microsecond=0)
      item = result[int(index / 2)]

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
  rates = create_rate_data(period_from, period_to, [2, 4, 6])
  consumption_key = 'consumption'
  latest_total_sum = 3

  # Act
  result = build_cost_statistics(
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
    expected_sum += round((consumptions[index]["consumption"] * rates[index]["value_inc_vat"]) / 100, 2)
    expected_state += round((consumptions[index]["consumption"] * rates[index]["value_inc_vat"]) / 100, 2)
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
async def test_when_half_hourly_costs_are_fractions_of_pennies_then_sum_is_not_skewed_by_rounding():
  # Arrange
  period_from = datetime.strptime("2022-02-28T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  current = datetime.strptime("2022-02-28T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")

  # Realistic low overnight consumption where each half hour costs a fraction of a penny.
  # Rounding each half hour to the nearest penny before summing skews the total
  # (e.g. 48 slots of 0.028 kWh at 26.4159p/kWh sum to £0.48 instead of £0.38).
  consumptions = []
  current_valid_from = period_from
  while current_valid_from < period_to:
    current_valid_to = current_valid_from + timedelta(minutes=30)
    consumptions.append({
      "start": current_valid_from,
      "end": current_valid_to,
      "consumption": 0.028
    })
    current_valid_from = current_valid_to

  rates = create_rate_data(period_from, period_to, [26.4159])
  consumption_key = 'consumption'
  latest_total_sum = 0

  # Act
  result = build_cost_statistics(
    current,
    consumptions,
    rates,
    consumption_key,
    latest_total_sum
  )

  # Assert
  assert result is not None

  expected_total = sum(
    consumption_cost_in_pence(consumptions[index]["consumption"], rates[index]["value_inc_vat"])
    for index in range(len(consumptions))
  ) / 100

  assert result[-1]["sum"] == pytest.approx(expected_total)
  assert result[-1]["state"] == pytest.approx(expected_total)
