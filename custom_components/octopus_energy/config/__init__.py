from ..utils import get_active_tariff_code

def get_meter_tariffs(account_info, now):
  meters = {}
  if account_info is not None and len(account_info["electricity_meter_points"]) > 0:
    for point in account_info["electricity_meter_points"]:
      active_tariff_code = get_active_tariff_code(now, point["agreements"])
      if active_tariff_code is not None:
        meters[point["mpan"]] = active_tariff_code

  return meters