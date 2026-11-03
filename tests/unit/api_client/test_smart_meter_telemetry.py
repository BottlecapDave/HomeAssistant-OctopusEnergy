from datetime import datetime, timedelta

import pytest

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException
from custom_components.octopus_energy.api_client.smart_meter_telemetry import (
  SmartMeterTelemetryResponseError,
  normalize_smart_meter_telemetry_response,
)


def telemetry_response(telemetry):
  return {
    "data": {
      "smartMeterTelemetry": telemetry
    }
  }


class FakeResponse:
  async def __aenter__(self):
    return self

  async def __aexit__(self, exc_type, exc, traceback):
    return None


class FakeClientSession:
  def post(self, *args, **kwargs):
    return FakeResponse()


def create_api_client(response_body):
  client = OctopusEnergyApiClient("NOT_REAL")

  async def async_refresh_token():
    return None

  async def async_create_client_session():
    return FakeClientSession()

  async def async_read_response(response, url):
    return response_body

  client.async_refresh_token = async_refresh_token
  client._create_client_session = async_create_client_session
  client.__async_read_response__ = async_read_response
  return client


@pytest.mark.parametrize("telemetry", [None, []])
def test_when_telemetry_is_empty_then_empty_list_returned(telemetry):
  result = normalize_smart_meter_telemetry_response(telemetry_response(telemetry))

  assert result == []


@pytest.mark.parametrize("response", [
  None,
  [],
  {},
  {"data": None},
  {"data": {}},
  telemetry_response({}),
])
def test_when_response_shape_is_invalid_then_error_raised(response):
  with pytest.raises(SmartMeterTelemetryResponseError):
    normalize_smart_meter_telemetry_response(response)


def test_when_rows_are_out_of_order_then_valid_rows_are_sorted_and_invalid_timestamps_are_skipped():
  result = normalize_smart_meter_telemetry_response(telemetry_response([
    {"readAt": "not-a-date", "consumptionDelta": "100"},
    {"readAt": "2025-08-01T01:00:00+00:00", "consumptionDelta": "300"},
    {"readAt": None, "consumptionDelta": "200"},
    {"readAt": "2025-08-01T00:30:00+00:00", "consumptionDelta": "100"},
    {"readAt": "2025-08-01T00:00:00", "consumptionDelta": "50"},
  ]))

  assert [reading["start"] for reading in result] == [
    datetime.fromisoformat("2025-08-01T00:30:00+00:00"),
    datetime.fromisoformat("2025-08-01T01:00:00+00:00"),
  ]
  assert result[0]["end"] == result[0]["start"] + timedelta(minutes=30)


def test_when_values_are_valid_then_units_and_signs_are_preserved():
  result = normalize_smart_meter_telemetry_response(telemetry_response([{
    "readAt": "2025-08-01T00:00:00+00:00",
    "consumption": "12345",
    "consumptionDelta": 0,
    "demand": -250,
    "export": 0,
  }]))

  assert result == [{
    "total_consumption": 12.345,
    "total_export": 0,
    "consumption": 0,
    "demand": -250,
    "start": datetime.fromisoformat("2025-08-01T00:00:00+00:00"),
    "end": datetime.fromisoformat("2025-08-01T00:30:00+00:00"),
  }]


def test_when_optional_values_are_missing_or_not_finite_then_safe_defaults_are_returned():
  result = normalize_smart_meter_telemetry_response(telemetry_response([{
    "readAt": "2025-08-01T00:00:00+00:00",
    "consumption": float("nan"),
    "consumptionDelta": None,
    "demand": float("inf"),
    "export": True,
  }]))

  assert result[0]["total_consumption"] is None
  assert result[0]["total_export"] is None
  assert result[0]["consumption"] == 0
  assert result[0]["demand"] is None


@pytest.mark.parametrize("consumption_delta", [None, float("nan"), float("inf"), True, "invalid"])
def test_when_consumption_delta_is_missing_or_invalid_then_zero_returned(consumption_delta):
  result = normalize_smart_meter_telemetry_response(telemetry_response([{
    "readAt": "2025-08-01T00:00:00+00:00",
    "consumptionDelta": consumption_delta,
    "demand": 100,
  }]))

  assert result[0]["consumption"] == 0
  assert result[0]["demand"] == 100


def test_when_duplicate_timestamps_are_returned_then_later_non_null_values_win():
  result = normalize_smart_meter_telemetry_response(telemetry_response([
    {
      "readAt": "2025-08-01T00:00:00+00:00",
      "consumption": "1000",
      "consumptionDelta": "100",
      "demand": "200",
      "export": "3000",
    },
    {
      "readAt": "2025-08-01T00:00:00+00:00",
      "consumption": "2000",
      "consumptionDelta": "250",
      "demand": None,
      "export": "4000",
    },
  ]))

  assert len(result) == 1
  assert result[0]["total_consumption"] == 2
  assert result[0]["total_export"] == 4
  assert result[0]["consumption"] == 0.25
  assert result[0]["demand"] == 200


def test_when_later_duplicate_has_null_delta_then_earlier_delta_is_preserved():
  result = normalize_smart_meter_telemetry_response(telemetry_response([
    {
      "readAt": "2025-08-01T00:00:00+00:00",
      "consumptionDelta": "100",
    },
    {
      "readAt": "2025-08-01T00:00:00+00:00",
      "consumptionDelta": None,
      "demand": "250",
    },
  ]))

  assert len(result) == 1
  assert result[0]["consumption"] == 0.1
  assert result[0]["demand"] == 250


@pytest.mark.asyncio
async def test_when_api_returns_null_telemetry_then_empty_list_returned():
  client = create_api_client(telemetry_response(None))
  period_from = datetime.fromisoformat("2025-08-01T00:00:00+00:00")

  result = await client.async_get_smart_meter_consumption(
    "device-id",
    period_from,
    period_from + timedelta(days=1)
  )

  assert result == []


@pytest.mark.asyncio
async def test_when_api_returns_malformed_telemetry_then_request_exception_raised():
  client = create_api_client({"data": {}})
  period_from = datetime.fromisoformat("2025-08-01T00:00:00+00:00")

  with pytest.raises(RequestException) as raised:
    await client.async_get_smart_meter_consumption(
      "device-id",
      period_from,
      period_from + timedelta(days=1)
    )

  assert raised.value.errors == ["Response does not contain smart meter telemetry"]

@pytest.mark.asyncio
async def test_when_api_returns_out_of_period_telemetry_then_it_is_filtered():
  client = create_api_client(telemetry_response([
    { "readAt": "2025-07-31T23:30:00+00:00", "demand": 100 },
    { "readAt": "2025-08-01T00:00:00+00:00", "demand": 200 },
    { "readAt": "2025-08-02T00:00:00+00:00", "demand": 300 },
  ]))
  period_from = datetime.fromisoformat("2025-08-01T00:00:00+00:00")

  result = await client.async_get_smart_meter_consumption(
    "device-id",
    period_from,
    period_from + timedelta(days=1)
  )

  assert [item["demand"] for item in result] == [200]
