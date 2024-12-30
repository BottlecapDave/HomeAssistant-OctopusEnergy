import pytest

from integration import get_test_context
from custom_components.octopus_energy.api_client import AuthenticationException, OctopusEnergyApiClient, RequestException

@pytest.mark.asyncio
async def test_when_get_account_is_called_then_electricity_and_gas_points_returned():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = context.account_id

    # Act
    account = await client.async_get_account(account_id)

    # Assert
    assert account is not None
    assert "electricity_meter_points" in account
    
    assert len(account["electricity_meter_points"]) == 1
    meter_point = account["electricity_meter_points"][0]
    assert meter_point["mpan"] == context.electricity_mpan
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert meter["is_export"] == False
    assert meter["is_smart_meter"] == True
    assert meter["serial_number"] == context.electricity_serial_number
    assert meter["manufacturer"] is not None
    assert meter["model"] is not None
    assert meter["firmware"] is not None

    assert "agreements" in meter_point
    assert len(meter_point["agreements"]) > 0
    for agreement in meter_point["agreements"]:
        assert "tariff_code" in agreement
        assert "start" in agreement
        assert "end" in agreement
    
    assert "gas_meter_points" in account
    assert len(account["gas_meter_points"]) == 1
    meter_point = account["gas_meter_points"][0]
    assert meter_point["mprn"] == context.gas_mprn
    
    assert len(meter_point["meters"]) == 1
    meter = meter_point["meters"][0]
    assert meter["is_smart_meter"] == True
    assert meter["serial_number"] == context.gas_serial_number
    assert meter["manufacturer"] is not None
    assert meter["model"] is not None
    assert meter["firmware"] is not None

    assert "agreements" in meter_point
    assert len(meter_point["agreements"]) > 0
    for agreement in meter_point["agreements"]:
        assert "tariff_code" in agreement
        assert "start" in agreement
        assert "end" in agreement

    assert "octoplus_enrolled" in account

    assert "heat_pump_ids" in account
    assert account["heat_pump_ids"] is not None
    assert len(account["heat_pump_ids"]) >= 0

@pytest.mark.asyncio
async def test_when_get_account_is_called_and_not_found_then_exception_is_raised():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient(context.api_key)
    account_id = "not-an-account"

    # Act
    exception_raised = False
    try:
        await client.async_get_account(account_id)
    except AuthenticationException:
        exception_raised = True

    # Assert
    assert exception_raised == True

@pytest.mark.asyncio
async def test_when_get_account_is_called_and_api_key_is_invalid_then_exception_is_raised():
    # Arrange
    context = get_test_context()

    client = OctopusEnergyApiClient("invalid_api_key")
    account_id = context.account_id

    # Act
    exception_raised = False
    try:
        await client.async_get_account(account_id)
    except AuthenticationException:
        exception_raised = True

    # Assert
    assert exception_raised == True