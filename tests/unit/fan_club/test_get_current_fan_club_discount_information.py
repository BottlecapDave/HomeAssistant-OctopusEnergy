from datetime import (datetime, timedelta)
import pytest

from unit.fan_club import (create_discount_data)
from custom_components.octopus_energy.fan_club import get_current_fan_club_discount_information

@pytest.mark.asyncio
async def test_when_target_has_no_discounts_and_gmt_then_no_discount_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-03-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T04:00:01Z", "%Y-%m-%dT%H:%M:%S%z")

  discount_data = create_discount_data(period_from, period_to, [1])

  # Act
  discount_information = get_current_fan_club_discount_information(discount_data, now)

  # Assert
  assert discount_information is None

@pytest.mark.asyncio
async def test_when_target_has_no_discounts_and_bst_then_no_discount_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-03-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T05:00:01+01:00", "%Y-%m-%dT%H:%M:%S%z")

  discount_data = create_discount_data(period_from, period_to, [1])

  # Act
  discount_information = get_current_fan_club_discount_information(discount_data, now)

  # Assert
  assert discount_information is None

@pytest.mark.asyncio
async def test_when_target_has_discounts_and_gmt_then_discount_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-03-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T03:10:01Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_discount = 10
  expected_max_discount = 30
  expected_discount = 20

  discount_data = create_discount_data(period_from, period_to, [expected_min_discount, expected_discount, expected_discount, expected_max_discount])

  total_discount_value = 0
  total_discounts = 0
  today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
  today_end = today_start + timedelta(days=1)
  for discount in discount_data:
    if discount.start >= today_start and discount.end <= today_end:
      total_discount_value += discount.discount
      total_discounts += 1

  # Act
  discount_information = get_current_fan_club_discount_information(discount_data, now)

  # Assert
  assert discount_information is not None

  assert discount_information["start"] == datetime.strptime("2022-03-01T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert discount_information["end"] == discount_information["start"] + timedelta(minutes=60)
  assert discount_information["discount"] == expected_discount
  
  assert "min_discount_today" in discount_information
  assert discount_information["min_discount_today"] == expected_min_discount
  
  assert "max_discount_today" in discount_information
  assert discount_information["max_discount_today"] == expected_max_discount
  
  assert "average_discount_today" in discount_information
  assert discount_information["average_discount_today"] == (total_discount_value / total_discounts)

@pytest.mark.asyncio
async def test_when_target_has_discounts_and_bst_then_discount_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-03-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T04:10:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
  expected_min_discount = 10
  expected_max_discount = 30
  expected_discount = 20

  discount_data = create_discount_data(period_from, period_to, [expected_min_discount, expected_discount, expected_discount, expected_max_discount])

  total_discount_value = 0
  total_discounts = 0
  today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
  today_end = today_start + timedelta(days=1)
  for discount in discount_data:
    if discount.start >= today_start and discount.end <= today_end:
      total_discount_value += discount.discount
      total_discounts += 1

  # Act
  discount_information = get_current_fan_club_discount_information(discount_data, now)

  # Assert
  assert discount_information is not None

  assert discount_information["start"] == datetime.strptime("2022-03-01T02:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
  assert discount_information["end"] == discount_information["start"] + timedelta(minutes=60)
  assert discount_information["discount"] == expected_discount
  
  assert "min_discount_today" in discount_information
  assert discount_information["min_discount_today"] == expected_min_discount
  
  assert "max_discount_today" in discount_information
  assert discount_information["max_discount_today"] == expected_max_discount
  
  assert "average_discount_today" in discount_information
  assert discount_information["average_discount_today"] == (total_discount_value / total_discounts)

@pytest.mark.asyncio
async def test_when_all_discounts_identical_costs_then_discount_information_is_returned():
  # Arrange
  period_from = datetime.strptime("2022-03-01T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  period_to = datetime.strptime("2022-03-01T04:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
  now = datetime.strptime("2022-03-01T03:10:01Z", "%Y-%m-%dT%H:%M:%S%z")
  expected_discount = 20

  discount_data = create_discount_data(period_from, period_to, [expected_discount])

  total_discount_value = 0
  total_discounts = 0
  today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
  today_end = today_start + timedelta(days=1)
  for discount in discount_data:
    if discount.start >= today_start and discount.end <= today_end:
      total_discount_value += discount.discount
      total_discounts += 1

  # Act
  discount_information = get_current_fan_club_discount_information(discount_data, now)

  # Assert
  assert discount_information is not None

  assert discount_information["start"] == period_from
  assert discount_information["end"] == period_to
  assert discount_information["discount"] == expected_discount
  
  assert "min_discount_today" in discount_information
  assert discount_information["min_discount_today"] == expected_discount
  
  assert "max_discount_today" in discount_information
  assert discount_information["max_discount_today"] == expected_discount
  
  assert "average_discount_today" in discount_information
  assert discount_information["average_discount_today"] == (total_discount_value / total_discounts)
