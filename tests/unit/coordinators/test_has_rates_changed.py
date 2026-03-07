
from datetime import datetime, timedelta

from custom_components.octopus_energy.coordinators import has_rates_changed
from tests.unit import create_rate_data

def test_when_old_rates_and_new_rates_different_length_then_true_returned():
    period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    old_rates = create_rate_data(period_from, period_to + timedelta(hours=12), [1, 2])
    new_rates = create_rate_data(period_from, period_to + timedelta(hours=11), [1, 2])

    assert len(old_rates) != len(new_rates)
    assert has_rates_changed(old_rates, new_rates) is True

def test_when_old_rates_and_new_rates_same_length_but_different_rate_then_true_returned():
    period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    old_rates = create_rate_data(period_from, period_to, [1, 2])
    new_rates = create_rate_data(period_from, period_to, [1, 3])

    assert len(old_rates) == len(new_rates)
    assert has_rates_changed(old_rates, new_rates) is True

def test_when_old_rates_and_new_rates_same_length_but_start_then_true_returned():
    period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    old_rates = create_rate_data(period_from, period_to, [1, 2])
    new_rates = create_rate_data(period_from, period_to, [1, 2])
    new_rates[0]["start"] -= timedelta(minutes=30)

    assert len(old_rates) == len(new_rates)
    assert has_rates_changed(old_rates, new_rates) is True

def test_when_old_rates_and_new_rates_same_length_but_end_then_true_returned():
    period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    old_rates = create_rate_data(period_from, period_to, [1, 2])
    new_rates = create_rate_data(period_from, period_to, [1, 2])
    new_rates[0]["end"] -= timedelta(minutes=30)

    assert len(old_rates) == len(new_rates)
    assert has_rates_changed(old_rates, new_rates) is True

def test_when_old_rates_and_new_rates_same_length_and_same_rate_then_false_returned():
    period_from = datetime.strptime(f'2024-11-19T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    period_to = datetime.strptime(f'2024-11-20T00:00:00Z', "%Y-%m-%dT%H:%M:%S%z")
    old_rates = create_rate_data(period_from, period_to, [1, 2])
    new_rates = create_rate_data(period_from, period_to, [1, 2])

    assert len(old_rates) == len(new_rates)
    assert has_rates_changed(old_rates, new_rates) is False