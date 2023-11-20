import logging
from datetime import datetime, timedelta

from homeassistant.util.dt import (now)
from homeassistant.helpers.update_coordinator import (
  DataUpdateCoordinator
)

from ..const import (
  COORDINATOR_REFRESH_IN_SECONDS,
  DOMAIN,
  DATA_CLIENT,
  DATA_ACCOUNT_ID,
  DATA_WHEEL_OF_FORTUNE_SPINS,
)

from ..api_client import OctopusEnergyApiClient
from ..api_client.saving_sessions import SavingSession
from ..api_client.wheel_of_fortune import WheelOfFortuneSpinsResponse

_LOGGER = logging.getLogger(__name__)

class WheelOfFortuneSpinsCoordinatorResult:
  last_retrieved: datetime
  spins: WheelOfFortuneSpinsResponse

  def __init__(self, last_retrieved: datetime, spins: WheelOfFortuneSpinsResponse):
    self.last_retrieved = last_retrieved
    self.spins = spins

async def async_refresh_wheel_of_fortune_spins(
    current: datetime,
    client: OctopusEnergyApiClient,
    account_id: str,
    existing_result: WheelOfFortuneSpinsCoordinatorResult
) -> WheelOfFortuneSpinsCoordinatorResult:
  if existing_result is None or current.minute % 30 == 0:
    try:
      result = await client.async_get_wheel_of_fortune_spins(account_id)

      return WheelOfFortuneSpinsCoordinatorResult(current, result)
    except:
      _LOGGER.debug('Failed to retrieve wheel of fortune spins')
  
  return existing_result

async def async_setup_wheel_of_fortune_spins_coordinator(hass, account_id: str):
  async def async_update_data():
    """Fetch data from API endpoint."""
    current = now()
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]

    hass.data[DOMAIN][DATA_WHEEL_OF_FORTUNE_SPINS] = await async_refresh_wheel_of_fortune_spins(
      current,
      client,
      account_id,
      hass.data[DOMAIN][DATA_WHEEL_OF_FORTUNE_SPINS] if DATA_WHEEL_OF_FORTUNE_SPINS in hass.data[DOMAIN] else None
    )

    return hass.data[DOMAIN][DATA_WHEEL_OF_FORTUNE_SPINS]

  coordinator = DataUpdateCoordinator(
    hass,
    _LOGGER,
    name=f"{account_id}_wheel_of_fortune_spins",
    update_method=async_update_data,
    # Because of how we're using the data, we'll update every minute, but we will only actually retrieve
    # data every 30 minutes
    update_interval=timedelta(seconds=COORDINATOR_REFRESH_IN_SECONDS),
    always_update=True
  )
  
  await coordinator.async_config_entry_first_refresh()

  return coordinator