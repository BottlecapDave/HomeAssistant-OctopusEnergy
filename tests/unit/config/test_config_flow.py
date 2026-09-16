from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from custom_components.octopus_energy.config_flow import OctopusEnergyConfigFlow
from custom_components.octopus_energy.const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_KIND,
  CONFIG_KIND_ACCOUNT,
  CONFIG_KIND_TARIFF_COMPARISON,
  CONFIG_MAIN_API_KEY,
  CONFIG_TARIFF_COMPARISON_MPAN_MPRN,
  CONFIG_TARIFF_COMPARISON_NAME,
  CONFIG_TARIFF_COMPARISON_PRODUCT_CODE,
  CONFIG_TARIFF_COMPARISON_TARIFF_CODE,
  DATA_ACCOUNT,
  DATA_CLIENT,
  DOMAIN,
)


def configure_update_helpers(flow: OctopusEnergyConfigFlow) -> None:
  flow.async_update_and_abort = Mock(return_value={"type": "abort"})
  flow.async_update_reload_and_abort = Mock(return_value={"type": "abort"})


@pytest.mark.asyncio
async def test_reconfigure_account_updates_without_explicit_reload():
  config_entry = SimpleNamespace(data={
    CONFIG_KIND: CONFIG_KIND_ACCOUNT,
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_MAIN_API_KEY: "old-api-key",
  })
  flow = OctopusEnergyConfigFlow()
  flow._get_reconfigure_entry = Mock(return_value=config_entry)
  configure_update_helpers(flow)

  with patch(
    "custom_components.octopus_energy.config_flow.async_validate_main_config",
    new=AsyncMock(return_value={}),
  ):
    result = await flow.async_step_reconfigure_account({
      CONFIG_MAIN_API_KEY: "new-api-key",
    })

  assert result == {"type": "abort"}
  flow.async_update_and_abort.assert_called_once_with(
    config_entry,
    data_updates={
      CONFIG_KIND: CONFIG_KIND_ACCOUNT,
      CONFIG_ACCOUNT_ID: "A-TEST",
      CONFIG_MAIN_API_KEY: "new-api-key",
    },
  )
  flow.async_update_reload_and_abort.assert_not_called()


@pytest.mark.asyncio
async def test_reconfigure_tariff_comparison_updates_without_explicit_reload():
  config_entry = SimpleNamespace(data={
    CONFIG_KIND: CONFIG_KIND_TARIFF_COMPARISON,
    CONFIG_ACCOUNT_ID: "A-TEST",
    CONFIG_TARIFF_COMPARISON_NAME: "Current tariff",
    CONFIG_TARIFF_COMPARISON_MPAN_MPRN: "1234567890123",
    CONFIG_TARIFF_COMPARISON_PRODUCT_CODE: "CURRENT-PRODUCT",
    CONFIG_TARIFF_COMPARISON_TARIFF_CODE: "CURRENT-TARIFF",
  })
  flow = OctopusEnergyConfigFlow()
  flow.hass = SimpleNamespace(data={
    DOMAIN: {
      "A-TEST": {
        DATA_ACCOUNT: SimpleNamespace(account={}),
        DATA_CLIENT: Mock(),
      },
    },
  })
  flow._get_reconfigure_entry = Mock(return_value=config_entry)
  configure_update_helpers(flow)

  with patch(
    "custom_components.octopus_energy.config_flow.async_validate_tariff_comparison_config",
    new=AsyncMock(return_value={}),
  ):
    result = await flow.async_step_reconfigure_tariff_comparison({
      CONFIG_TARIFF_COMPARISON_NAME: "Updated tariff",
    })

  assert result == {"type": "abort"}
  flow.async_update_and_abort.assert_called_once_with(
    config_entry,
    data_updates={
      **config_entry.data,
      CONFIG_TARIFF_COMPARISON_NAME: "Updated tariff",
    },
  )
  flow.async_update_reload_and_abort.assert_not_called()
