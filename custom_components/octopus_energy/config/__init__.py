from ..utils import Tariff, get_active_tariff

def get_electricity_meter_tariffs(account_info, now) -> "dict[str, Tariff]":
  meters = {}
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff = get_active_tariff(now, point["agreements"])
      if active_tariff is not None:
        meters[point["mpan"]] = active_tariff

  return meters

def get_gas_meter_tariffs(account_info, now) -> "dict[str, Tariff]":
  meters = {}
  if account_info is not None and len(account_info["gas_meter_points"]) > 0:
    for point in account_info["gas_meter_points"]:
      active_tariff = get_active_tariff(now, point["agreements"])
      if active_tariff is not None:
        meters[point["mprn"]] = active_tariff

  return meters