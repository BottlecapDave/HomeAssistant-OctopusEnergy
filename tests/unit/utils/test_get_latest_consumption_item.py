from datetime import datetime

import pytest

from custom_components.octopus_energy.utils.consumption import get_latest_consumption_item


@pytest.mark.parametrize("consumption", [None, [], [{ "end": datetime(2026, 8, 1), "total_consumption": None }]])
def test_when_no_non_null_value_is_available_then_none_returned(consumption):
  assert get_latest_consumption_item(consumption, "total_consumption") is None


def test_when_data_is_unsorted_then_newest_non_null_item_returned():
  consumption = [
    { "end": datetime(2026, 8, 1, 1), "total_consumption": None },
    { "end": datetime(2026, 8, 1, 0), "total_consumption": 10 },
    { "end": datetime(2026, 8, 1, 2), "total_consumption": 20 },
    { "end": datetime(2026, 8, 1, 3), "total_consumption": None },
  ]

  assert get_latest_consumption_item(consumption, "total_consumption") == consumption[2]


def test_when_newest_non_null_value_is_zero_then_item_returned():
  consumption = [
    { "end": datetime(2026, 8, 1, 0), "total_export": 10 },
    { "end": datetime(2026, 8, 1, 1), "total_export": 0 },
  ]

  assert get_latest_consumption_item(consumption, "total_export") == consumption[1]
