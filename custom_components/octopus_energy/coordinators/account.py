import logging
from datetime import timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from homeassistant.helpers import issue_registry as ir

from ..const import (
  DOMAIN,

  DATA_CLIENT,
  DATA_ACCOUNT,
  DATA_ACCOUNT_COORDINATOR,
)

from ..api_client import OctopusEnergyApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_account_info_coordinator(hass, account_id: str):
  if DATA_ACCOUNT_COORDINATOR in hass.data[DOMAIN]:
    _LOGGER.info("Account coordinator has already been configured, so skipping")
    return
  
  async def async_update_account_data():
    """Fetch data from API endpoint."""
    # Only get data every half hour or if we don't have any data
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    if (DATA_ACCOUNT not in hass.data[DOMAIN] or (current.minute % 30) == 0):

      account_info = None
      try:
        account_info = await client.async_get_account(account_id)

        if account_info is None:
          ir.async_create_issue(
            hass,
            DOMAIN,
            f"account_not_found_{account_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.ERROR,
            learn_more_url="https://github.com/BottlecapDave/HomeAssistant-OctopusEnergy/blob/develop/_docs/repairs/account_not_found.md",
            translation_key="account_not_found",
            translation_placeholders={ "account_id": account_id },
          )
        else:
          ir.async_delete_issue(hass, DOMAIN, f"account_not_found_{account_id}")
          hass.data[DOMAIN][DATA_ACCOUNT] = account_info

      except:
        # count exceptions as failure to retrieve account
        _LOGGER.debug('Failed to retrieve account information')
    
    return hass.data[DOMAIN][DATA_ACCOUNT]

  hass.data[DOMAIN][DATA_ACCOUNT_COORDINATOR] = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name="update_account",
    update_method=async_update_account_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(minutes=1),
  )
  
  await hass.data[DOMAIN][DATA_ACCOUNT_COORDINATOR].async_config_entry_first_refresh()