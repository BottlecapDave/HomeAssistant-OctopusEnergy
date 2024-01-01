"""Diagnostics support."""
import logging

from homeassistant.components.diagnostics import async_redact_data

from .const import (
  CONFIG_ACCOUNT_ID,
  DOMAIN,

  DATA_CLIENT
)

_LOGGER = logging.getLogger(__name__)

async def async_get_device_diagnostics(hass, entry, device):
    """Return diagnostics for a device."""

    config = dict(entry.data)

    if entry.options:
      config.update(entry.options)

    account_id = config[CONFIG_ACCOUNT_ID]

    client = hass.data[DOMAIN][account_id][DATA_CLIENT]

    _LOGGER.info('Retrieving account details for diagnostics...')
    
    account_info = await client.async_get_account(account_id)

    points_length = account_info is not None and len(account_info["electricity_meter_points"])
    if account_info is not None and points_length > 0:
      for point_index in range(points_length):
        account_info["electricity_meter_points"][point_index] = async_redact_data(account_info["electricity_meter_points"][point_index], { "mpan" })
        meters_length = len(account_info["electricity_meter_points"][point_index]["meters"])
        for meter_index in range(meters_length):
          account_info["electricity_meter_points"][point_index]["meters"][meter_index] = async_redact_data(account_info["electricity_meter_points"][point_index]["meters"][meter_index], { "serial_number", "device_id" })

    points_length = account_info is not None and len(account_info["gas_meter_points"])
    if account_info is not None and points_length > 0:
      for point_index in range(points_length):
        account_info["gas_meter_points"][point_index] = async_redact_data(account_info["gas_meter_points"][point_index], { "mprn" })
        meters_length = len(account_info["gas_meter_points"][point_index]["meters"])
        for meter_index in range(meters_length):
          account_info["gas_meter_points"][point_index]["meters"][meter_index] = async_redact_data(account_info["gas_meter_points"][point_index]["meters"][meter_index], { "serial_number", "device_id" })
    
    _LOGGER.info(f'Returning diagnostic details; {len(account_info["electricity_meter_points"])} electricity meter point(s), {len(account_info["gas_meter_points"])} gas meter point(s)')

    return account_info