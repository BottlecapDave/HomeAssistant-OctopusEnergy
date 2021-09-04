from homeassistant.config_entries import ConfigFlow
import voluptuous as vol
import logging

from .const import (
  DOMAIN,
  
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_ACCOUNT_ID,
  
  CONFIG_TARGET_NAME,
  CONFIG_TARGET_HOURS,
  CONFIG_TARGET_TYPE,
  CONFIG_TARGET_START_TIME,
  CONFIG_TARGET_END_TIME
)

import homeassistant.helpers.config_validation as cv
from .api_client import OctopusEnergyApiClient

ACCOUNT_DATA_SCHEMA = vol.Schema({
  vol.Required(CONFIG_MAIN_API_KEY): str,
  vol.Required(CONFIG_MAIN_ACCOUNT_ID): str,
})

TARGET_DATA_SCHEMA = vol.Schema({
  vol.Required(CONFIG_TARGET_NAME): str,
  vol.Required(CONFIG_TARGET_HOURS): str,
  vol.Required(CONFIG_TARGET_TYPE, default="Continuous"): vol.In({
    "Continuous": "Continuous",
    "Intermittent": "Intermittent"
  }),
  vol.Optional(CONFIG_TARGET_START_TIME): str,
  vol.Optional(CONFIG_TARGET_END_TIME): str,
})

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyConfigFlow(ConfigFlow, domain=DOMAIN): 
  """Config flow."""

  VERSION = 1

  async def async_setup_initial_account(self, user_input):
    """Setup the initial account based on the provided user input"""
    errors = {}

    client = OctopusEnergyApiClient(user_input[CONFIG_MAIN_API_KEY])
    account_info = await client.async_get_account(user_input[CONFIG_MAIN_ACCOUNT_ID])
    if (account_info == None):
      errors[CONFIG_MAIN_ACCOUNT_ID] = "account_not_found"
      return self.async_show_form(
        step_id="user", data_schema=ACCOUNT_DATA_SCHEMA, errors=errors
      )

    config = {
      CONFIG_MAIN_API_KEY: user_input[CONFIG_MAIN_API_KEY],
      CONFIG_MAIN_ACCOUNT_ID: user_input[CONFIG_MAIN_ACCOUNT_ID]
    }

    # Setup our basic sensors
    return self.async_create_entry(
      title="Octopus Energy", 
      data=config
    )

  async def async_setup_target(self, user_input):
    """Setup a target based on the provided user input"""
    errors = {}
    config = {
      CONFIG_TARGET_NAME: user_input[CONFIG_TARGET_NAME],
      CONFIG_TARGET_HOURS: user_input[CONFIG_TARGET_HOURS],
      CONFIG_TARGET_TYPE: user_input[CONFIG_TARGET_TYPE]
    }

    if CONFIG_TARGET_START_TIME in user_input:
      config[CONFIG_TARGET_START_TIME] = user_input[CONFIG_TARGET_START_TIME]

    if CONFIG_TARGET_END_TIME in user_input:
      config[CONFIG_TARGET_END_TIME] = user_input[CONFIG_TARGET_END_TIME]

    if len(errors) < 1:
      # Setup our targets sensor
      return self.async_create_entry(
        title=f"{config[CONFIG_TARGET_NAME]} (target)", 
        data=config
      )

    # Reshow our form with raised logins
    return self.async_show_form(
      step_id="user", data_schema=TARGET_DATA_SCHEMA, errors=errors
    )

  async def async_step_user(self, user_input):
    """Setup based on user config"""

    is_account_setup = False
    for entry in self._async_current_entries(include_ignore=False):
      if CONFIG_MAIN_API_KEY in entry.data:
        is_account_setup = True
        break

    if user_input is not None:
      # We are setting up our initial stage
      if CONFIG_MAIN_API_KEY in user_input:
        return await self.async_setup_initial_account(user_input)

      # We are setting up a target
      if CONFIG_TARGET_NAME in user_input:
        return await self.async_setup_target(user_input)

    if is_account_setup:
      return self.async_show_form(
        step_id="user", data_schema=TARGET_DATA_SCHEMA
      )

    return self.async_show_form(
      step_id="user", data_schema=ACCOUNT_DATA_SCHEMA
    )