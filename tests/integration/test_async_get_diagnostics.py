from datetime import datetime
import pytest

from homeassistant.util.dt import (utcnow)

from integration import get_test_context
from custom_components.octopus_energy.api_client import OctopusEnergyApiClient
from custom_components.octopus_energy.diagnostics import async_get_diagnostics

def assert_meter(meter, expected_serial_number: int):
  assert meter["is_smart_meter"] == True
  assert meter["serial_number"] == expected_serial_number
  assert meter["manufacturer"] is not None
  assert meter["model"] is not None
  assert meter["firmware"] is not None
  assert meter["device_id"] == "**REDACTED**"
  assert isinstance(meter["latest_consumption"], datetime)

  if meter["latest_device_consumption"] != "Not available":
    if meter["latest_device_consumption"]["total_consumption"] is not None:
        assert isinstance(meter["latest_device_consumption"]["total_consumption"], float)

    if meter["latest_device_consumption"]["consumption"] is not None:
        assert isinstance(meter["latest_device_consumption"]["consumption"], float)
    
    assert "demand" in meter["latest_device_consumption"]
    assert isinstance(meter["latest_device_consumption"]["start"], datetime)
    assert isinstance(meter["latest_device_consumption"]["end"], datetime)

@pytest.mark.asyncio
async def test_when_async_get_diagnostics_called_then_account_info_is_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    now = utcnow()

    def get_entity_info(redacted_mappings):
        return {
            "foo": {
                "last_updated": now,
                "last_changed": now,
            }
        }

    # Act
    data = await async_get_diagnostics(client, account_id, None, None, get_entity_info)

    # Assert
    assert data is not None
    account = data["account"]
    assert account is not None

    assert "id" in account
    assert account["id"] == "**REDACTED**"

    assert "electricity_meter_points" in account
    
    assert len(account["electricity_meter_points"]) == 1
    meter_point = account["electricity_meter_points"][0]
    assert meter_point["mpan"] == 2
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert meter["is_export"] == False
    assert_meter(meter, 1)

    assert "agreements" in meter_point
    assert len(meter_point["agreements"]) > 0
    for agreement in meter_point["agreements"]:
        assert "tariff_code" in agreement
        assert "start" in agreement
        assert "end" in agreement
    
    assert "gas_meter_points" in account
    assert len(account["gas_meter_points"]) == 1
    meter_point = account["gas_meter_points"][0]
    assert meter_point["mprn"] == 4
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert_meter(meter, 3)

    assert "agreements" in meter_point
    assert len(meter_point["agreements"]) > 0
    for agreement in meter_point["agreements"]:
        assert "tariff_code" in agreement
        assert "start" in agreement
        assert "end" in agreement

    assert "octoplus_enrolled" in account

    assert "entities" in data
    assert data["entities"]["foo"]["last_updated"] == now
    assert data["entities"]["foo"]["last_changed"] == now

    assert "intelligent_devices" in data

    assert "heat_pumps" in data

@pytest.mark.asyncio
async def test_when_async_get_diagnostics_called_and_account_exists_then_account_info_is_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id
    existing_account = await client.async_get_account(account_id)

    now = utcnow()

    def get_entity_info(redacted_mappings):
        return {
            "foo": {
                "last_updated": now,
                "last_changed": now,
            }
        }

    # Act
    data = await async_get_diagnostics(client, account_id, existing_account, None, get_entity_info)

    # Assert
    assert data is not None
    account = data["account"]
    assert account is not None
    assert account != existing_account

    assert "id" in account
    assert account["id"] == "**REDACTED**"

    assert "electricity_meter_points" in account
    
    assert len(account["electricity_meter_points"]) == 1
    meter_point = account["electricity_meter_points"][0]
    assert meter_point["mpan"] == 2
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert meter["is_export"] == False
    assert_meter(meter, 1)

    assert "agreements" in meter_point
    assert len(meter_point["agreements"]) > 0
    for agreement in meter_point["agreements"]:
        assert "tariff_code" in agreement
        assert "start" in agreement
        assert "end" in agreement
    
    assert "gas_meter_points" in account
    assert len(account["gas_meter_points"]) == 1
    meter_point = account["gas_meter_points"][0]
    assert meter_point["mprn"] == 4
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert_meter(meter, 3)

    assert "agreements" in meter_point
    assert len(meter_point["agreements"]) > 0
    for agreement in meter_point["agreements"]:
        assert "tariff_code" in agreement
        assert "start" in agreement
        assert "end" in agreement

    assert "octoplus_enrolled" in account

    assert "entities" in data
    assert data["entities"]["foo"]["last_updated"] == now
    assert data["entities"]["foo"]["last_changed"] == now

    assert "intelligent_devices" in data

    assert "heat_pumps" in data
