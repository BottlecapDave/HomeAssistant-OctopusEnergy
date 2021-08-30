from homeassistant.config_entries import ConfigFlow
import voluptuous as vol
import logging

from .const import (
  DOMAIN,
  
  CONFIG_API_KEY,
  CONFIG_TARIFF,
  CONFIG_TARIFF_CODE,
  CONFIG_ELEC_MPAN,
  CONFIG_ELEC_SN,
  CONFIG_GAS_MPRN,
  CONFIG_GAS_SN
)

DATA_SCHEMA = vol.Schema({
  vol.Required(CONFIG_API_KEY): str,
  vol.Required(CONFIG_TARIFF, default="Agile"): vol.In({
    "Agile": "Agile",
    "Go": "Go",
    "Other": "Other"
  }),
  vol.Required(CONFIG_TARIFF_CODE): str,
  vol.Optional(CONFIG_ELEC_MPAN): str,
  vol.Optional(CONFIG_ELEC_SN): str,
  vol.Optional(CONFIG_GAS_MPRN): str,
  vol.Optional(CONFIG_GAS_SN): str,
})

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = 1

  def __init__(self):
    """Initialize flow."""
    self._config = None

  async def async_step_user(self, info):

    if self._async_current_entries():
      return self.async_abort(reason="single_instance_allowed")

    errors = {}
    if info is not None:
      self._config = {
        CONFIG_API_KEY: info[CONFIG_API_KEY],
        CONFIG_TARIFF: info[CONFIG_TARIFF],
        CONFIG_TARIFF_CODE: info[CONFIG_TARIFF_CODE]
      }

      if (CONFIG_ELEC_MPAN in info and CONFIG_ELEC_SN not in info) or (CONFIG_ELEC_MPAN not in info and CONFIG_ELEC_SN in info):
        errors[CONFIG_ELEC_MPAN] = "both_electric_not_supplied"

      if CONFIG_ELEC_MPAN in info and CONFIG_ELEC_SN in info:
        self._config[CONFIG_ELEC_MPAN] = info[CONFIG_ELEC_MPAN]
        self._config[CONFIG_ELEC_SN] = info[CONFIG_ELEC_SN]

      if (CONFIG_GAS_MPRN in info and CONFIG_GAS_SN not in info) or (CONFIG_GAS_MPRN not in info and CONFIG_GAS_SN in info):
        errors[CONFIG_GAS_MPRN] = "both_gas_not_supplied"
        
      if CONFIG_GAS_MPRN in info and CONFIG_GAS_SN in info:
        self._config[CONFIG_GAS_MPRN] = info[CONFIG_GAS_MPRN]
        self._config[CONFIG_GAS_SN] = info[CONFIG_GAS_SN]

      if len(errors) < 1 and len(self._config) > 0:
        return self.async_create_entry(
          title="Octopus Energy", 
          data=self._config
        )

    return self.async_show_form(
      step_id="user", data_schema=DATA_SCHEMA, errors=errors
    )