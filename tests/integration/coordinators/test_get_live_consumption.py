# from datetime import datetime, timedelta
# import pytest
# import time

# from homeassistant.util.dt import (as_utc)

# from integration import (get_test_context)

# from custom_components.octopus_energy.sensor_utils import async_get_live_consumption
# from custom_components.octopus_energy.api_client import OctopusEnergyApiClient

# @pytest.mark.asyncio
# async def test_when_get_live_consumption_is_called_then_last_5_minutes_returned_returned():
#   # Arrange
#   context = get_test_context()
#   client = OctopusEnergyApiClient(context.api_key)
#   account_id = context.account_id

#   # Get our target device
#   account = await client.async_get_account(account_id)
  
#   assert account is not None
#   assert "electricity_meter_points" in account
  
#   assert len(account["electricity_meter_points"]) == 1
#   meter_point = account["electricity_meter_points"][0]
#   assert meter_point["mpan"] == context.electricity_mpan
    
#   assert len(meter_point["meters"]) == 1
#   meter = meter_point["meters"][0]
#   assert meter["device_id"] is not None

#   start_time = as_utc(datetime(2023, 1, 21, 0, 0))
#   end_time = start_time + timedelta(hours=1)
#   current_time = start_time

#   index = 0
#   minutes = 0
#   minutes_between_calls = 1
#   while current_time < end_time:
#     expected_start_at = start_time - timedelta(minutes=minutes_between_calls) + timedelta(minutes=minutes)

#     result = await async_get_live_consumption(client, current_time, meter["device_id"])
    
#     assert result is not None
#     assert "consumption" in result
#     assert result["consumption"] >= 0

#     assert "startAt" in result
#     assert result["startAt"] == expected_start_at

#     current_time = current_time + timedelta(minutes=minutes_between_calls)
#     index += 1
#     if (index >= minutes_between_calls):
#       index = 0
#       minutes += minutes_between_calls

#     # Sleep to make sure we don't get API errors
#     time.sleep(1)


