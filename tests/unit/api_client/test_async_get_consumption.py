import json
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.util.dt import parse_datetime

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, integration_context_header


@pytest.mark.asyncio
@pytest.mark.parametrize("fuel", ["electricity", "gas"])
async def test_consumption_response_is_parsed_filtered_and_sorted(fuel):
  client = OctopusEnergyApiClient("test-api-key")
  response = Mock(status=200)
  response.request_info.headers = {integration_context_header: f"{fuel}-consumption"}
  response.text = AsyncMock(return_value=json.dumps({"results": [
    {"consumption": "2.5", "interval_start": "2026-10-01T00:30:00Z", "interval_end": "2026-10-01T01:00:00Z"},
    {"consumption": "1.5", "interval_start": "2026-10-01T00:00:00Z", "interval_end": "2026-10-01T00:30:00Z"},
    {"consumption": "3.5", "interval_start": "2026-10-01T01:00:00Z", "interval_end": "2026-10-01T01:30:00Z"},
  ]}))
  session = Mock()
  session.get.return_value.__aenter__ = AsyncMock(return_value=response)
  session.get.return_value.__aexit__ = AsyncMock(return_value=False)
  period_from = parse_datetime("2026-10-01T00:00:00Z")
  period_to = parse_datetime("2026-10-01T01:00:00Z")

  with patch.object(client, "_create_client_session", AsyncMock(return_value=session)):
    result = await getattr(client, f"async_get_{fuel}_consumption")(
      "1234567890", "meter-serial", period_from, period_to,
    )

  assert result == [
    {"consumption": 1.5, "start": period_from, "end": parse_datetime("2026-10-01T00:30:00Z")},
    {"consumption": 2.5, "start": parse_datetime("2026-10-01T00:30:00Z"), "end": period_to},
  ]
  session.get.assert_called_once()
  assert f"/{fuel}-meter-points/1234567890/meters/meter-serial/consumption?" in session.get.call_args.args[0]
  assert session.get.call_args.kwargs["headers"] == {integration_context_header: f"{fuel}-consumption"}
