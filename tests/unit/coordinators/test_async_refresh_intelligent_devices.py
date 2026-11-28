from datetime import datetime, timedelta
import pytest
import mock

from custom_components.octopus_energy.const import REPAIR_INTELLIGENT_DEVICE_REMOVED
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.api_client.intelligent_device import IntelligentDevice
from custom_components.octopus_energy.coordinators.intelligent_device import IntelligentDeviceCoordinatorResult, async_refresh_devices
from custom_components.octopus_energy.utils.repairs import safe_repair_key

current = datetime.strptime("2023-07-14T10:30:01+01:00", "%Y-%m-%dT%H:%M:%S%z")
account_id = "A-XXXXXX"

def get_device(device_id: str):
  return IntelligentDevice(device_id, "provider", "make", "model", 75.0, 7.4, "ELECTRIC_VEHICLES")

@pytest.mark.asyncio
@pytest.mark.parametrize("retrieved_device_ids", [
  [],
  ["device-2"],
])
async def test_when_device_is_no_longer_returned_then_removed_repair_is_raised_for_that_device(retrieved_device_ids: list[str]):
  # Arrange
  retrieved_devices = [get_device(device_id) for device_id in retrieved_device_ids]
  current_devices = [get_device("device-1")] + retrieved_devices
  previous_request = IntelligentDeviceCoordinatorResult(current - timedelta(days=1), 1, current_devices)

  async def async_mocked_get_intelligent_devices(*args, **kwargs):
    return retrieved_devices

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_intelligent_devices=async_mocked_get_intelligent_devices):
    with mock.patch("custom_components.octopus_energy.coordinators.intelligent_device.ir") as issue_registry:
      result = await async_refresh_devices(
        None,
        current,
        OctopusEnergyApiClient("NOT_REAL"),
        account_id,
        current_devices,
        False,
        previous_request
      )

  # Assert
  assert result.devices == retrieved_devices

  created_keys = [call.args[2] for call in issue_registry.async_create_issue.call_args_list]
  assert created_keys == [safe_repair_key(REPAIR_INTELLIGENT_DEVICE_REMOVED, "device-1")]
