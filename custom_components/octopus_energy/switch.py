from datetime import timedelta
import logging

from homeassistant.util.dt import (utcnow)

from .intelligent.smart_charge import OctopusEnergyIntelligentSmartCharge
from .intelligent.bump_charge import OctopusEnergyIntelligentBumpCharge
from .api_client import OctopusEnergyApiClient
from .intelligent import is_intelligent_tariff
from .utils import get_active_tariff_code

from .const import (
  DATA_ACCOUNT_ID,
  DATA_CLIENT,
  DOMAIN,

  CONFIG_MAIN_API_KEY,

  DATA_INTELLIGENT_SETTINGS_COORDINATOR,
  DATA_INTELLIGENT_DISPATCHES_COORDINATOR,
  DATA_ACCOUNT
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=1)

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

  if has_intelligent_tariff:
    settings_coordinator = hass.data[DOMAIN][DATA_INTELLIGENT_SETTINGS_COORDINATOR]
    dispatches_coordinator = hass.data[DOMAIN][DATA_INTELLIGENT_DISPATCHES_COORDINATOR]
    client: OctopusEnergyApiClient = hass.data[DOMAIN][DATA_CLIENT]
    account_id = hass.data[DOMAIN][DATA_ACCOUNT_ID]
    device = await client.async_get_intelligent_device(hass.data[DOMAIN][DATA_ACCOUNT_ID])
    async_add_entities([
      OctopusEnergyIntelligentSmartCharge(hass, settings_coordinator, client, device, account_id),
      OctopusEnergyIntelligentBumpCharge(hass, dispatches_coordinator, client, device, account_id)
    ], True)