import logging

from .const import (
  DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry):
  """This is called from the config flow."""

  # Forward our entry to setup our default sensors
  hass.async_create_task(
    hass.config_entries.async_forward_entry_setup(entry, "sensor")
  )

  return True