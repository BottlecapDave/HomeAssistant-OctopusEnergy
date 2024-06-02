import pytest
from datetime import datetime

from custom_components.octopus_energy.statistics import get_statistic_ids_to_remove

def get_account_info():
  return {
    "electricity_meter_points": [
      {
        "mpan": 'elec-mpan',
        "agreements": [
          {
            "start": "2023-08-01T00:00:00+01:00",
            "end": "2023-08-14T00:00:00+01:00",
            "tariff_code": "E-1R-SUPER-GREEN-24M-21-07-30-C",
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ],
        "meters": [
          {
            "serial_number": 'elec-sn',
            "is_export": True,
          }
        ]
      }
    ],
    "gas_meter_points": [
      {
        "mprn": 'gas-mprn',
        "agreements": [
          {
            "start": "2023-08-13T00:00:00+01:00",
            "end": "2023-09-01T00:00:00+01:00",
            "tariff_code": "G-1R-SUPER-GREEN-24M-21-07-30-C",
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ],
        "meters": [
          {
            "serial_number": 'gas-sn'
          }
        ]
      }
    ]
  }

def test_when_account_info_is_none_then_empty_list_returned():
  # Arrange
  now = datetime.strptime("2023-08-13T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  account_info = None

  # Act
  result = get_statistic_ids_to_remove(now, account_info)

  # Assert
  assert len(result) == 0

def test_when_all_meters_have_valid_tariff_then_empty_list_returned():
  # Arrange
  now = datetime.strptime("2023-08-13T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  account_info = get_account_info()

  # Act
  result = get_statistic_ids_to_remove(now, account_info)

  # Assert
  assert len(result) == 0

def test_when_electricity_meter_have_valid_tariff_then_electricity_meters_returned():
  # Arrange
  now = datetime.strptime("2023-08-15T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  account_info = get_account_info()

  # Act
  result = get_statistic_ids_to_remove(now, account_info)

  # Assert
  assert len(result) == 3
  assert result[0] == "octopus_energy:electricity_elec-sn_elec-mpan_export_previous_accumulative_consumption"
  assert result[1] == "octopus_energy:electricity_elec-sn_elec-mpan_export_previous_accumulative_cost"
  assert result[2] == "octopus_energy:electricity_elec-sn_elec-mpan_previous_accumulative_cost"

def test_when_gas_meter_have_valid_tariff_then_gas_meters_returned():
  # Arrange
  now = datetime.strptime("2023-08-12T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  account_info = get_account_info()

  # Act
  result = get_statistic_ids_to_remove(now, account_info)

  # Assert
  assert len(result) == 2
  assert result[0] == "octopus_energy:gas_gas-sn_gas-mprn_previous_accumulative_consumption"
  assert result[1] == "octopus_energy:gas_gas-sn_gas-mprn_previous_accumulative_cost"

def test_when_electricity_and_gas_meter_have_valid_tariff_then_electricity_and_gas_meters_returned():
  # Arrange
  now = datetime.strptime("2023-09-02T00:00:00+01:00", "%Y-%m-%dT%H:%M:%S%z")
  account_info = get_account_info()

  # Act
  result = get_statistic_ids_to_remove(now, account_info)

  # Assert
  assert len(result) == 5
  assert result[0] == "octopus_energy:electricity_elec-sn_elec-mpan_export_previous_accumulative_consumption"
  assert result[1] == "octopus_energy:electricity_elec-sn_elec-mpan_export_previous_accumulative_cost"
  assert result[2] == "octopus_energy:electricity_elec-sn_elec-mpan_previous_accumulative_cost"
  assert result[3] == "octopus_energy:gas_gas-sn_gas-mprn_previous_accumulative_consumption"
  assert result[4] == "octopus_energy:gas_gas-sn_gas-mprn_previous_accumulative_cost"
