import pytest
import mock
from datetime import datetime, timedelta

from custom_components.octopus_energy.const import REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS
from custom_components.octopus_energy.coordinators.fan_club_discounts import FanClubDiscountCoordinatorResult, async_refresh_fan_club_discounts
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.fan_club import FanClubStatusItem, DiscountPeriod, ForecastData, ForecastInfo, FanClubResponse 

fan_club_discounts = [
  FanClubStatusItem(discountSource="Fan #1",
                    current=DiscountPeriod(startAt=datetime.strptime(f'2024-02-04T00:30:00Z', "%Y-%m-%dT%H:%M:%S%z"), discount="0.5"),
                    historic=[DiscountPeriod(startAt=datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z"), discount="0.5")],
                    forecast=ForecastInfo(baseTime=datetime.strptime(f'2024-02-04T01:00:00Z', "%Y-%m-%dT%H:%M:%S%z"), data=[
                      ForecastData(validTime=datetime.strptime(f'2024-02-04T01:00:00Z', "%Y-%m-%dT%H:%M:%S%z"), projectedDiscount="0.5")
                    ])),
]

@pytest.mark.asyncio
async def test_when_next_refresh_is_in_the_future_and_previous_data_is_available_then_previous_data_returned():
  # Arrange
  client = OctopusEnergyApiClient("NOT_REAL")
  current_utc_timestamp = datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  account_id = "ABC"

  previous_data = FanClubDiscountCoordinatorResult(current_utc_timestamp, 1, fan_club_discounts)

  # Act
  result = await async_refresh_fan_club_discounts(
    current_utc_timestamp,
    account_id,
    client,
    previous_data
  )

  # Assert
  assert result == previous_data

@pytest.mark.asyncio
async def test_when_results_retrieved_then_results_returned():
  # Arrange
  previous_data = None
  account_id = "ABC"
    
  current_utc_timestamp = datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  
  expected_result = fan_club_discounts
  mock_api_called = False
  async def async_mocked_get_fan_club_discounts(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    return FanClubResponse(fanClubStatus=expected_result)

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_fan_club_discounts=async_mocked_get_fan_club_discounts): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_fan_club_discounts(
      current_utc_timestamp,
      account_id,
      client,
      previous_data
    )

    # Assert
    assert result is not None
    assert result.last_evaluated == current_utc_timestamp
    assert result.next_refresh == current_utc_timestamp.replace(second=0, microsecond=0) + timedelta(minutes=REFRESH_RATE_IN_MINUTES_FAN_CLUB_DISCOUNTS)
    assert result.discounts is not None

    for actual in result.discounts:
      assert actual.source == fan_club_discounts[0].discountSource

      expected_start = fan_club_discounts[0].historic[0].startAt
      for actual_discount in actual.discounts:
        assert actual_discount.start == expected_start
        expected_start = expected_start + timedelta(minutes=30)
        assert actual_discount.end == expected_start
        assert actual_discount.discount == 50

    assert mock_api_called == True

@pytest.mark.asyncio
async def test_when_exception_raised_then_existing_results_returned_and_exception_captured():
  # Arrange
  account_id = "ABC"
  current_utc_timestamp = datetime.strptime(f'2024-02-04T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
  previous_data = FanClubDiscountCoordinatorResult(current_utc_timestamp - timedelta(days=1), 1, fan_club_discounts)
  
  mock_api_called = False
  raised_exception = RequestException("My exception", [])
  async def async_mocked_get_fan_club_discounts(*args, **kwargs):
    nonlocal mock_api_called
    mock_api_called = True
    raise raised_exception

  with mock.patch.multiple(OctopusEnergyApiClient, async_get_fan_club_discounts=async_mocked_get_fan_club_discounts): 
    client = OctopusEnergyApiClient("NOT_REAL")

    # Act
    result = await async_refresh_fan_club_discounts(
      current_utc_timestamp,
      account_id,
      client,
      previous_data
    )

    # Assert
    assert mock_api_called == True

    assert result is not None
    assert result.last_evaluated == previous_data.last_evaluated
    assert result.last_error == raised_exception
    assert result.discounts == previous_data.discounts
    assert result.request_attempts == previous_data.request_attempts + 1
    assert result.next_refresh == previous_data.next_refresh + timedelta(minutes=1)
