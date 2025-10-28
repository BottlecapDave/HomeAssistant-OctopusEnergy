from datetime import datetime, timedelta
import pytest

from custom_components.octopus_energy.api_client.fan_club import DiscountPeriod, FanClubStatusItem, ForecastInfo, ForecastData
from custom_components.octopus_energy.fan_club import combine_discounts, Discount

@pytest.mark.asyncio
async def test_when_status_has_historic_current_and_forecast_data_then_all_discounts_are_combined():
    # Arrange
    now = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # Create historic discount periods (2 entries)
    historic = [
        DiscountPeriod(startAt=now - timedelta(hours=1), discount="0.500"),
        DiscountPeriod(startAt=now - timedelta(minutes=30), discount="0.500")
    ]
    
    # Create current discount period
    current = DiscountPeriod(startAt=now + timedelta(minutes=10), discount="0.500")
    
    # Create forecast data (2 entries)
    forecast_data = [
        ForecastData(validTime=now + timedelta(hours=1), projectedDiscount="0.500"),
        ForecastData(validTime=now + timedelta(hours=2), projectedDiscount="0.500")
    ]
    
    forecast = ForecastInfo(baseTime=now, data=forecast_data)
    
    # Create the status item
    status = FanClubStatusItem(
        discountSource="#1 Fan: Test Farm",
        current=current,
        historic=historic,
        forecast=forecast
    )
    
    # Act
    result = combine_discounts(status)
    
    # Assert
    assert result is not None
    assert len(result) == 8  # 2 historic + 1 current + 4 forecast (2 entries * 2 30-min periods each)
    
    expected_start = datetime.strptime("2022-03-01T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    for item in result:
        assert item.start == expected_start
        expected_start += timedelta(minutes=30)
        assert item.end == expected_start
        assert item.discount == 50

@pytest.mark.asyncio
async def test_when_forecast_is_none_then_all_discounts_are_combined():
    # Arrange
    now = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # Create historic discount periods (2 entries)
    historic = [
        DiscountPeriod(startAt=now - timedelta(hours=1), discount="0.500"),
        DiscountPeriod(startAt=now - timedelta(minutes=30), discount="0.500")
    ]
    
    # Create current discount period
    current = DiscountPeriod(startAt=now + timedelta(minutes=10), discount="0.500")
    
    forecast = None
    
    # Create the status item
    status = FanClubStatusItem(
        discountSource="#1 Fan: Test Farm",
        current=current,
        historic=historic,
        forecast=forecast
    )
    
    # Act
    result = combine_discounts(status)
    
    # Assert
    assert result is not None
    assert len(result) == 4
    
    expected_start = datetime.strptime("2022-03-01T11:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    for item in result:
        assert item.start == expected_start
        expected_start += timedelta(minutes=30)
        assert item.end == expected_start
        assert item.discount == 50

@pytest.mark.asyncio
async def test_when_status_has_only_current_data_then_two_discounts_are_returned():
    # Arrange
    now = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # Create current discount period
    current = DiscountPeriod(startAt=now + timedelta(minutes=10), discount="0.200")
    
    # Create empty historic and forecast
    historic = []
    forecast = ForecastInfo(baseTime=now, data=[])
    
    # Create the status item
    status = FanClubStatusItem(
        discountSource="#1 Fan: Test Farm",
        current=current,
        historic=historic,
        forecast=forecast
    )
    
    # Act
    result = combine_discounts(status)
    
    # Assert
    assert result is not None
    assert len(result) == 2  # Only current entry
    
    expected_start = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    for item in result:
        assert item.start == expected_start
        expected_start += timedelta(minutes=30)
        assert item.end == expected_start
        assert item.discount == 20

@pytest.mark.asyncio
async def test_when_status_has_only_current_data_after_thirty_minute_then_two_discounts_are_returned():
    # Arrange
    now = datetime.strptime("2022-03-01T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # Create current discount period
    current = DiscountPeriod(startAt=now, discount="0.200")
    
    # Create empty historic and forecast
    historic = []
    forecast = ForecastInfo(baseTime=now, data=[])
    
    # Create the status item
    status = FanClubStatusItem(
        discountSource="#1 Fan: Test Farm",
        current=current,
        historic=historic,
        forecast=forecast
    )
    
    # Act
    result = combine_discounts(status)
    
    # Assert
    assert result is not None
    assert len(result) == 1  # Only current entry
    
    expected_start = datetime.strptime("2022-03-01T12:30:00Z", "%Y-%m-%dT%H:%M:%S%z")
    for item in result:
        assert item.start == expected_start
        expected_start += timedelta(minutes=30)
        assert item.end == expected_start
        assert item.discount == 20

@pytest.mark.asyncio
async def test_when_discount_values_vary_then_correct_values_are_calculated():
    # Arrange
    now = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # Create historic with different discount values
    historic = [
        DiscountPeriod(startAt=now - timedelta(hours=1), discount="0.000"),
        DiscountPeriod(startAt=now - timedelta(minutes=30), discount="0.200")
    ]
    
    # Create current discount period with different value
    current = DiscountPeriod(startAt=now + timedelta(minutes=10), discount="0.500")
    
    # Create forecast with different values
    forecast_data = [
        ForecastData(validTime=now + timedelta(hours=1), projectedDiscount="0.200"),
        ForecastData(validTime=now + timedelta(hours=2), projectedDiscount="0.000")
    ]
    
    forecast = ForecastInfo(baseTime=now, data=forecast_data)
    
    # Create the status item
    status = FanClubStatusItem(
        discountSource="#1 Fan: Test Farm",
        current=current,
        historic=historic,
        forecast=forecast
    )
    
    # Act
    result = combine_discounts(status)
    
    # Assert
    assert result is not None
    assert len(result) == 8

    expected_discounts = [0.0, 20.0, 50.0, 50.0, 20.0, 20.0, 0.0, 0.0]
    for i in range(len(result)):
        assert result[i].discount == expected_discounts[i]

@pytest.mark.asyncio
async def test_when_forecast_has_multiple_entries_then_each_generates_two_discount_periods():
    # Arrange
    now = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    
    # No historic data
    historic = []
    
    # Create current discount period
    current = DiscountPeriod(startAt=now + timedelta(minutes=10), discount="0.500")
    
    # Create forecast with three entries
    forecast_data = [
        ForecastData(validTime=now + timedelta(hours=1), projectedDiscount="0.500"),
        ForecastData(validTime=now + timedelta(hours=2), projectedDiscount="0.500"),
        ForecastData(validTime=now + timedelta(hours=3), projectedDiscount="0.500")
    ]
    
    forecast = ForecastInfo(baseTime=now, data=forecast_data)
    
    # Create the status item
    status = FanClubStatusItem(
        discountSource="#1 Fan: Test Farm",
        current=current,
        historic=historic,
        forecast=forecast
    )
    
    # Act
    result = combine_discounts(status)
    
    # Assert
    assert result is not None
    assert len(result) == 8  # 1 current + 6 forecast periods (3 entries * 2 periods each)
    
    expected_start = datetime.strptime("2022-03-01T12:00:00Z", "%Y-%m-%dT%H:%M:%S%z")
    for item in result:
        assert item.start == expected_start
        expected_start += timedelta(minutes=30)
        assert item.end == expected_start
        assert item.discount == 50