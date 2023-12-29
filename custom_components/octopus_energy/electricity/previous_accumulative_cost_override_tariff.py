import logging

from homeassistant.core import HomeAssistant

from homeassistant.components.text import TextEntity

from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.helpers.entity import generate_entity_id, DeviceInfo

from ..const import (DOMAIN, REGEX_TARIFF_PARTS)

from . import get_electricity_tariff_override_key

from ..utils.tariff_check import check_tariff_override_valid

from ..api_client import OctopusEnergyApiClient

from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPreviousAccumulativeElectricityCostTariffOverride(OctopusEnergyElectricitySensor, TextEntity, RestoreEntity):
  """Sensor for the tariff for the previous days accumulative electricity cost looking at a different tariff."""

  _attr_pattern = REGEX_TARIFF_PARTS

  def __init__(self, hass: HomeAssistant, account_id: str, client: OctopusEnergyApiClient, tariff_code, meter, point):
    """Init sensor."""
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point)

    self.entity_id = generate_entity_id("text.{}", self.unique_id, hass=hass)

    self._hass = hass

    self._client = client
    self._tariff_code = tariff_code
    self._attr_native_value = tariff_code
    self._account_id = account_id
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_accumulative_cost_override_tariff"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Electricity {self._serial_number} {self._mpan}{self._export_name_addition} Previous Cost Override Tariff"
  
  @property
  def icon(self):
    """Icon of the sensor."""
    return "mdi:currency-gbp"

  async def async_set_value(self, value: str) -> None:
    """Update the value."""
    result = await check_tariff_override_valid(self._client, self._tariff_code, value)
    if (result is not None):
      raise Exception(result)

    self._attr_native_value = value
    self._hass.data[DOMAIN][self._account_id][get_electricity_tariff_override_key(self._serial_number, self._mpan)] = value
    self.async_write_ha_state()

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    state = await self.async_get_last_state()
    
    if state is not None:
      if state.state is not None:
        self._attr_native_value = state.state
        self._attr_state = state.state
        self._hass.data[DOMAIN][self._account_id][get_electricity_tariff_override_key(self._serial_number, self._mpan)] = self._attr_native_value
      
      self._attributes = dict_to_typed_dict(state.attributes)
    
      _LOGGER.debug(f'Restored OctopusEnergyPreviousAccumulativeElectricityCostTariffOverride state: {self._attr_state}')