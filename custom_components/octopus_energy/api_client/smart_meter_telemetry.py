from datetime import timedelta
from math import isfinite
from typing import Any

from homeassistant.util.dt import parse_datetime


class SmartMeterTelemetryResponseError(Exception):
  """Raised when a smart meter telemetry response has an invalid shape."""


def _parse_optional_number(value: Any, divisor: float = 1) -> float | None:
  if value is None or isinstance(value, bool):
    return None

  try:
    parsed_value = float(value)
  except (TypeError, ValueError):
    return None

  if isfinite(parsed_value) == False:
    return None

  return parsed_value / divisor


def normalize_smart_meter_telemetry_response(response_body: Any) -> list[dict]:
  """Normalize the smart meter telemetry contained in a GraphQL response."""
  if isinstance(response_body, dict) == False:
    raise SmartMeterTelemetryResponseError("Response body must be an object")

  data = response_body.get("data")
  if isinstance(data, dict) == False or "smartMeterTelemetry" not in data:
    raise SmartMeterTelemetryResponseError("Response does not contain smart meter telemetry")

  telemetry = data["smartMeterTelemetry"]
  if telemetry is None:
    return []
  if isinstance(telemetry, list) == False:
    raise SmartMeterTelemetryResponseError("Smart meter telemetry must be a list or null")

  readings_by_start = {}
  for item in telemetry:
    if isinstance(item, dict) == False:
      continue

    read_at = parse_datetime(item.get("readAt")) if isinstance(item.get("readAt"), str) else None
    if read_at is None or read_at.tzinfo is None or read_at.utcoffset() is None:
      continue

    total_consumption = _parse_optional_number(item.get("consumption"), 1000)
    total_export = _parse_optional_number(item.get("export"), 1000)
    consumption_delta = _parse_optional_number(item.get("consumptionDelta"), 1000)
    demand = _parse_optional_number(item.get("demand"))
    reading = {
      "total_consumption": total_consumption,
      "total_export": total_export,
      # The API can omit the delta from a row which still contains useful live
      # demand data. Preserve the existing zero fallback for those rows.
      "consumption": consumption_delta if consumption_delta is not None else 0,
      "demand": demand,
      "start": read_at,
      "end": read_at + timedelta(minutes=30),
    }

    existing_reading = readings_by_start.get(read_at)
    if existing_reading is None:
      readings_by_start[read_at] = reading
      continue

    later_values = {
      "total_consumption": total_consumption,
      "total_export": total_export,
      "consumption": consumption_delta,
      "demand": demand,
    }
    for key, value in later_values.items():
      if value is not None:
        existing_reading[key] = value

  return sorted(readings_by_start.values(), key=lambda reading: reading["start"])
