from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow)

from .intelligent.charge_limit import OctopusEnergyIntelligentChargeLimit
from .api_client import OctopusEnergyApiClient
from .intelligent import async_mock_intelligent_data, is_intelligent_tariff
from .utils import get_active_tariff_code

from .const import (
  DATA_ACCOUNT_ID,
  DATA_CLIENT,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
  """Setup sensors based on our entry"""

  if CONFIG_MAIN_API_KEY in entry.data:
    await async_setup_intelligent_sensors(hass, async_add_entities)

  return True

async def async_setup_intelligent_sensors(hass, async_add_entities):
  _LOGGER.debug('Setting up intelligent sensors')

  account_info = hass.data[DOMAIN][DATA_ACCOUNT]

  now = utcnow()
  has_intelligent_tariff = False
  if len(account_info["electricity_meter_points"]) > 0:

    for point in account_info["electricity_meter_points"]:
      # We only care about points that have active agreements
      tariff_code = get_active_tariff_code(now, point["agreements"])
      if is_intelligent_tariff(tariff_code):
        has_intelligent_tariff = True
        break

  if has_intelligent_tariff or await async_mock_intelligent_data(hass):
    coordinator = hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS_COORDINATOR]
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_id = hass.data[DOMAIN][DATA_ACCOUNT_ID]
    device = await client.async_get_intelligent_device(account_id)
    async_add_entities([
      OctopusEnergyIntelligentChargeLimit(hass, coordinator, client, device, account_id),
    ], True)