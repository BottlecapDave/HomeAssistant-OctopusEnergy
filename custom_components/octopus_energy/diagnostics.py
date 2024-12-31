"""Diagnostics support."""
import copy
from datetime import datetime, timedelta
import logging
from typing import Callable

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.helpers import entity_registry as er
from homeassistant.util.dt import (now)

from .const import (
  CONFIG_ACCOUNT_ID,
  DATA_ACCOUNT,
  DOMAIN,

  DATA_CLIENT
)
from .api_client import OctopusEnergyApiClient, TimeoutException
from .heat_pump import get_mock_heat_pump_id, mock_heat_pump_status_and_configuration
from .utils.debug_overrides import AccountDebugOverride, async_get_account_debug_override

_LOGGER = logging.getLogger(__name__)

async def async_get_device_consumption_data(client: OctopusEnergyApiClient, device_id: str):
  current: datetime = now()
  period_from = current - timedelta(minutes=120)
  period_to = current
  try:
    consumption_data = await client.async_get_smart_meter_consumption(
      device_id,
      period_from,
      period_to)
  
    if consumption_data is not None and len(consumption_data) > 0:
      return {
        "total_consumption": consumption_data[-1]["total_consumption"],
        "consumption": consumption_data[-1]["consumption"],
        "demand": consumption_data[-1]["demand"],
        "start": consumption_data[-1]["start"],
        "end": consumption_data[-1]["end"],
      }
    
    return "Not available"
  
  except Exception as e:
    return f"Failed to retrieve - {e}"

async def async_get_diagnostics(client: OctopusEnergyApiClient, account_id: str, existing_account_info: dict, account_debug_override: AccountDebugOverride | None, get_entity_info: Callable[[dict], dict]):
  _LOGGER.info('Retrieving account details for diagnostics...')

  if existing_account_info is None:
    account_info = await client.async_get_account(account_id)
  else:
    account_info = copy.deepcopy(existing_account_info)

  redacted_mappings = {}
  redacted_mapping_count = 1

  if account_info is not None:
    redacted_mappings[account_info["id"]] = "A"

  points_length = account_info is not None and len(account_info["electricity_meter_points"])
  if account_info is not None and points_length > 0:
    for point_index in range(points_length):
      meters_length = len(account_info["electricity_meter_points"][point_index]["meters"])
      for meter_index in range(meters_length):

        try:
          consumptions = await client.async_get_electricity_consumption(account_info["electricity_meter_points"][point_index]["mpan"], account_info["electricity_meter_points"][point_index]["meters"][meter_index]["serial_number"], page_size=1)
          account_info["electricity_meter_points"][point_index]["meters"][meter_index]["latest_consumption"] = consumptions[-1]["end"] if consumptions is not None and len(consumptions) > 0 else "Not available"
        except TimeoutException:
          account_info["electricity_meter_points"][point_index]["meters"][meter_index]["latest_consumption"] = "time out"

        device_id  = account_info["electricity_meter_points"][point_index]["meters"][meter_index]["device_id"]
        if device_id is not None and device_id != "":
          account_info["electricity_meter_points"][point_index]["meters"][meter_index]["device"] = await async_get_device_consumption_data(client, device_id)
        
        redacted_mappings[f"{account_info["electricity_meter_points"][point_index]["meters"][meter_index]["serial_number"]}"] = redacted_mapping_count
        account_info["electricity_meter_points"][point_index]["meters"][meter_index]["serial_number"] = redacted_mapping_count
        redacted_mapping_count += 1
        
        account_info["electricity_meter_points"][point_index]["meters"][meter_index] = async_redact_data(account_info["electricity_meter_points"][point_index]["meters"][meter_index], { "device_id" })
      
      redacted_mappings[f"{account_info["electricity_meter_points"][point_index]["mpan"]}"] = redacted_mapping_count
      account_info["electricity_meter_points"][point_index]["mpan"] = redacted_mapping_count
      redacted_mapping_count += 1

  points_length = account_info is not None and len(account_info["gas_meter_points"])
  if account_info is not None and points_length > 0:
    for point_index in range(points_length):
      meters_length = len(account_info["gas_meter_points"][point_index]["meters"])
      for meter_index in range(meters_length):
        
        try:
          consumptions = await client.async_get_gas_consumption(account_info["gas_meter_points"][point_index]["mprn"], account_info["gas_meter_points"][point_index]["meters"][meter_index]["serial_number"], page_size=1)
          account_info["gas_meter_points"][point_index]["meters"][meter_index]["latest_consumption"] = consumptions[-1]["end"] if consumptions is not None and len(consumptions) > 0 else "Not available"
        except TimeoutException:
          account_info["gas_meter_points"][point_index]["meters"][meter_index]["latest_consumption"] = "time out"

        device_id  = account_info["gas_meter_points"][point_index]["meters"][meter_index]["device_id"]
        if device_id is not None and device_id != "":
          account_info["gas_meter_points"][point_index]["meters"][meter_index]["device"] = await async_get_device_consumption_data(client, device_id)

        redacted_mappings[f"{account_info["gas_meter_points"][point_index]["meters"][meter_index]["serial_number"]}"] = redacted_mapping_count
        account_info["gas_meter_points"][point_index]["meters"][meter_index]["serial_number"] = redacted_mapping_count
        redacted_mapping_count += 1

        account_info["gas_meter_points"][point_index]["meters"][meter_index] = async_redact_data(account_info["gas_meter_points"][point_index]["meters"][meter_index], { "device_id" })

      redacted_mappings[f"{account_info["gas_meter_points"][point_index]["mprn"]}"] = redacted_mapping_count
      account_info["gas_meter_points"][point_index]["mprn"] = redacted_mapping_count
      redacted_mapping_count += 1

  intelligent_device = await client.async_get_intelligent_device(account_id)
  intelligent_settings = None
  if intelligent_device is not None:
    intelligent_settings = await client.async_get_intelligent_settings(account_id, intelligent_device.id)
  
  _LOGGER.info(f'Returning diagnostic details; {len(account_info["electricity_meter_points"])} electricity meter point(s), {len(account_info["gas_meter_points"])} gas meter point(s)')

  account_info = async_redact_data(account_info, { "id" }) if account_info is not None else None

  mock_heat_pump = account_debug_override.mock_heat_pump if account_debug_override is not None else False

  heat_pumps = {}
  if mock_heat_pump:
    heat_pump_id = get_mock_heat_pump_id()
    heat_pumps[heat_pump_id] = mock_heat_pump_status_and_configuration().dict()
  elif "heat_pump_ids" in account_info:
    for heat_pump_id in account_info["heat_pump_ids"]:
      try:
        heat_pump = await client.async_get_heat_pump_configuration_and_status(account_id, heat_pump_id)
        heat_pumps[heat_pump_id] = heat_pump.dict() if heat_pump is not None else "Not found"
      except Exception as e:
        heat_pumps[heat_pump_id] = f"Failed to retrieve - {e}"

  return {
    "account": account_info,
    "entities": get_entity_info(redacted_mappings),
    "intelligent_device": intelligent_device.to_dict() if intelligent_device is not None else None,
    "intelligent_settings": intelligent_settings.to_dict() if intelligent_settings is not None else None,
    "heat_pumps": heat_pumps,
  }

async def async_get_device_diagnostics(hass, entry, device):
    """Return diagnostics for a device."""

    config = dict(entry.data)

    if entry.options:
      config.update(entry.options)
    
    account_id = config[CONFIG_ACCOUNT_ID]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_debug_override = await async_get_account_debug_override(hass, account_id)

    def get_entity_info(redacted_mappings):
      entity_registry = er.async_get(hass)
      entities = entity_registry.entities.items()
      states = hass.states.async_all()
      entity_info = dict()
      for item in entities:
        unique_id: str = item[1].unique_id

        if "octopus_energy" in unique_id:
          state = None
          for s in states:
            if s.entity_id == item[1].entity_id:
              state = s
              break

          for key in redacted_mappings.keys():
            unique_id = unique_id.lower().replace(key.lower(), f"{redacted_mappings[key]}")
          
          entity_info[unique_id] = {
            "last_updated": state.last_updated if state is not None else None,
            "last_changed": state.last_changed if state is not None else None
          }

      return entity_info

    return await async_get_diagnostics(client, account_id, account_info, account_debug_override, get_entity_info)

async def async_get_config_entry_diagnostics(hass, entry):
    """Return diagnostics for a device."""

    config = dict(entry.data)

    if entry.options:
      config.update(entry.options)
    
    account_id = config[CONFIG_ACCOUNT_ID]
    account_result = hass.data[DOMAIN][account_id][DATA_ACCOUNT]
    account_info = account_result.account if account_result is not None else None
    client: OctopusEnergyApiClient = hass.data[DOMAIN][account_id][DATA_CLIENT]
    account_debug_override = await async_get_account_debug_override(hass, account_id)

    def get_entity_info(redacted_mappings):
      entity_registry = er.async_get(hass)
      entities = entity_registry.entities.items()
      states = hass.states.async_all()
      entity_info = dict()
      for item in entities:
        unique_id: str = item[1].unique_id

        if "octopus_energy" in unique_id:
          state = None
          for s in states:
            if s.entity_id == item[1].entity_id:
              state = s
              break

          for key in redacted_mappings.keys():
            unique_id = unique_id.lower().replace(key.lower(), f"{redacted_mappings[key]}")
          
          entity_info[unique_id] = {
            "last_updated": state.last_updated if state is not None else None,
            "last_changed": state.last_changed if state is not None else None
          }

      return entity_info

    return await async_get_diagnostics(client, account_id, account_info, account_debug_override, get_entity_info)