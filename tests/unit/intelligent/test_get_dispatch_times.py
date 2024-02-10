import pytest
from datetime import datetime

from custom_components.octopus_energy.utils import OffPeakTime, get_off_peak_times
from custom_components.octopus_energy.api_client import rates_to_thirty_minute_increments
from custom_components.octopus_energy.intelligent import get_dispatch_times
from custom_components.octopus_energy.api_client.intelligent_dispatches import IntelligentDispatchItem

@pytest.mark.asyncio
async def test_when_off_peak_times_and_planned_dispatches_is_none_then_empty_list_returned():
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  off_peak_times = None
  planned_dispatches = None
  
  # Act
  result = get_dispatch_times(current, off_peak_times, planned_dispatches)

  # Assert
  assert result is not None
  assert len(result) == 0
  
@pytest.mark.asyncio
async def test_when_off_peak_times_provided_then_current_and_future_times_returned():
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  off_peak_times = [
    OffPeakTime(datetime.strptime("2023-10-13T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    OffPeakTime(datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z")),
    OffPeakTime(datetime.strptime("2023-10-14T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z"))
	]
  planned_dispatches = None
  
  # Act
  result = get_dispatch_times(current, off_peak_times, planned_dispatches)

  # Assert
  assert result is not None
  assert len(result) == 2
  
  assert result[0].start == off_peak_times[1].start
  assert result[0].end == off_peak_times[1].end

  assert result[1].start == off_peak_times[2].start
  assert result[1].end == off_peak_times[2].end
  
@pytest.mark.asyncio
async def test_when_planned_dispatches_provided_then_current_and_future_times_returned():
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  off_peak_times = []
  planned_dispatches = [
    IntelligentDispatchItem(datetime.strptime("2023-10-13T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', ''),
    IntelligentDispatchItem(datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T01:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', ''),
    IntelligentDispatchItem(datetime.strptime("2023-10-14T02:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T03:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', '')
	]
  
  # Act
  result = get_dispatch_times(current, off_peak_times, planned_dispatches)

  # Assert
  assert result is not None
  assert len(result) == 2
  
  assert result[0].start == planned_dispatches[1].start
  assert result[0].end == planned_dispatches[1].end

  assert result[1].start == planned_dispatches[2].start
  assert result[1].end == planned_dispatches[2].end

@pytest.mark.asyncio
async def test_when_off_peak_overlaps_planned_dispatch_start_then_current_and_future_times_returned_and_combined():
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  off_peak_times = [
    OffPeakTime(datetime.strptime("2023-10-14T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-15T04:30:01Z", "%Y-%m-%dT%H:%M:%S%z"))
	]
  planned_dispatches = [
    IntelligentDispatchItem(datetime.strptime("2023-10-13T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', ''),
    IntelligentDispatchItem(datetime.strptime("2023-10-14T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T23:30:01Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', ''),
    IntelligentDispatchItem(datetime.strptime("2023-10-15T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T06:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', '')
	]
  
  # Act
  result = get_dispatch_times(current, off_peak_times, planned_dispatches)

  # Assert
  assert result is not None
  assert len(result) == 2
  
  assert result[0].start == planned_dispatches[1].start
  assert result[0].end == off_peak_times[0].end

  assert result[1].start == planned_dispatches[2].start
  assert result[1].end == planned_dispatches[2].end
  
@pytest.mark.asyncio
async def test_when_off_peak_overlaps_planned_dispatch_end_then_current_and_future_times_returned_and_combined():
  current = datetime.strptime("2023-10-14T00:00:01Z", "%Y-%m-%dT%H:%M:%S%z")
  off_peak_times = [
    OffPeakTime(datetime.strptime("2023-10-13T23:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T04:30:01Z", "%Y-%m-%dT%H:%M:%S%z"))
	]
  planned_dispatches = [
    IntelligentDispatchItem(datetime.strptime("2023-10-13T23:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T00:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', ''),
    IntelligentDispatchItem(datetime.strptime("2023-10-14T04:29:59Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-14T05:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', ''),
    IntelligentDispatchItem(datetime.strptime("2023-10-15T10:00:00Z", "%Y-%m-%dT%H:%M:%S%z"), datetime.strptime("2023-10-15T10:30:00Z", "%Y-%m-%dT%H:%M:%S%z"), 1, '', '')
	]
  
  # Act
  result = get_dispatch_times(current, off_peak_times, planned_dispatches)

  # Assert
  assert result is not None
  assert len(result) == 2
  
  assert result[0].start == off_peak_times[0].start
  assert result[0].end == planned_dispatches[1].end

  assert result[1].start == planned_dispatches[2].start
  assert result[1].end == planned_dispatches[2].end