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

  readings = []
  for item in telemetry:
    read_at = parse_datetime(item["readAt"])
    consumption_delta = _parse_optional_number(item.get("consumptionDelta"), 1000)
    readings.append({
      "total_consumption": _parse_optional_number(item.get("consumption"), 1000),
      "total_export": _parse_optional_number(item.get("export"), 1000),
      # The API can omit the delta from a row which still contains useful live
      # demand data. Preserve the existing zero fallback for those rows.
      "consumption": consumption_delta if consumption_delta is not None else 0,
      "demand": _parse_optional_number(item.get("demand")),
      "start": read_at,
      "end": read_at + timedelta(minutes=30),
    })

  return sorted(readings, key=lambda reading: reading["start"])
