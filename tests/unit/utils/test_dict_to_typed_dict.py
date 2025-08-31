from datetime import datetime

import pytz
import pytest

from custom_components.octopus_energy.utils.attributes import dict_to_typed_dict
from homeassistant.util.dt import (as_utc, parse_datetime, set_default_time_zone)

@pytest.mark.asyncio
async def test_when_none_is_provided_then_none_is_returned():
  # Arrange
  input = None

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input is None
  assert result is None

@pytest.mark.asyncio
async def test_when_key_is_skipped_attribute_then_left_as_string():
  # Arrange
  input = {
    "mprn": "1",
    "mpan": "2",
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["mprn"] == "1"
  assert input["mpan"] == "2"

  assert result is not None
  assert "mprn" in result
  assert result["mprn"] == "1"
  assert isinstance(result["mprn"], str)

  assert result["mpan"] == "2"
  assert isinstance(result["mpan"], str)

@pytest.mark.asyncio
async def test_when_key_is_ignored_then_not_returned():
  # Arrange
  input = {
    "mprn": "1",
    "mpan": "2",
  }

  # Act
  result = dict_to_typed_dict(input, ["mprn"])

  # Assert
  assert input["mprn"] == "1"
  assert input["mpan"] == "2"

  assert result is not None
  assert "mprn" not in result
  assert "mpan" in result

@pytest.mark.asyncio
async def test_when_default_ignore_key_is_present_then_not_returned():
  # Arrange
  input = {
    "mprn": "1",
    "last_evaluated": "2"
  }

  # Act
  result = dict_to_typed_dict(input, [])

  # Assert
  assert input["mprn"] == "1"
  assert input["last_evaluated"] == "2"

  assert result is not None
  assert "last_evaluated" not in result
  assert "mprn" in result

@pytest.mark.asyncio
async def test_when_int_is_present_then_converted_to_int():
  # Arrange
  input = {
    "foo": "1"
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"] == "1"

  assert result is not None
  assert "foo" in result
  assert result["foo"] == 1
  assert isinstance(result["foo"], int)

@pytest.mark.asyncio
async def test_when_float_is_present_then_converted_to_float():
  # Arrange
  input = {
    "foo": "1.010"
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"] == "1.010"

  assert result is not None
  assert "foo" in result
  assert result["foo"] == 1.010
  assert isinstance(result["foo"], float)

@pytest.mark.asyncio
async def test_when_utc_datetime_is_present_then_converted_to_datetime():
  # Arrange
  input = {
    "foo": "2023-11-16T20:00:00Z"
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"] == "2023-11-16T20:00:00Z"
  
  assert result is not None
  assert "foo" in result
  assert result["foo"] == datetime.strptime(input["foo"], "%Y-%m-%dT%H:%M:%S%z")
  assert isinstance(result["foo"], datetime)

@pytest.mark.asyncio
async def test_when_utc_datetime_is_present_during_bst_then_converted_to_correct_datetime():
  # Arrange
  set_default_time_zone(pytz.timezone('Europe/London'))

  input = {
    "foo": as_utc(parse_datetime("2025-03-30T22:00:00+00:00"))
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert result is not None
  assert "foo" in result
  assert isinstance(result["foo"], datetime)
  assert result["foo"].year == 2025
  assert result["foo"].month == 3
  assert result["foo"].day == 30
  assert result["foo"].hour == 23
  assert result["foo"].minute == 0
  assert result["foo"].second == 0

@pytest.mark.asyncio
async def test_when_datetime_with_timezone_is_present_then_converted_to_datetime():
  # Arrange
  input = {
    "foo": "2023-11-16T20:00:00+01:00"
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"] == "2023-11-16T20:00:00+01:00"

  assert result is not None
  assert "foo" in result
  assert result["foo"] == datetime.strptime(input["foo"], "%Y-%m-%dT%H:%M:%S%z")
  assert isinstance(result["foo"], datetime)

@pytest.mark.asyncio
async def test_when_inner_object_present_then_converted():
  # Arrange
  input = {
    "foo": {
      "bar1": "1",
      "bar2": "1.010",
      "bar3": "2023-11-16T20:00:00+01:00"
    }
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"]["bar1"] == "1"
  assert input["foo"]["bar2"] == "1.010"
  assert input["foo"]["bar3"] == "2023-11-16T20:00:00+01:00"

  assert result is not None
  assert "foo" in result
  
  assert "bar1" in result["foo"]
  assert result["foo"]["bar1"] == 1
  assert isinstance(result["foo"]["bar1"], int)

  assert "bar2" in result["foo"]
  assert result["foo"]["bar2"] == 1.01
  assert isinstance(result["foo"]["bar2"], float)

  assert "bar3" in result["foo"]
  assert result["foo"]["bar3"] == datetime.strptime(input["foo"]["bar3"], "%Y-%m-%dT%H:%M:%S%z")
  assert isinstance(result["foo"]["bar3"], datetime)

@pytest.mark.asyncio
async def test_when_array_present_then_converted():
  # Arrange
  input = {
    "foo": [
      {
        "bar1": "1",
        "bar2": "1.010",
        "bar3": "2023-11-16T20:00:00+01:00"
      }
    ]
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"][0]["bar1"] == "1"
  assert input["foo"][0]["bar2"] == "1.010"
  assert input["foo"][0]["bar3"] == "2023-11-16T20:00:00+01:00"

  assert result is not None
  assert "foo" in result

  assert len(result["foo"]) == 1
  
  assert "bar1" in result["foo"][0]
  assert result["foo"][0]["bar1"] == 1
  assert isinstance(result["foo"][0]["bar1"], int)

  assert "bar2" in result["foo"][0]
  assert result["foo"][0]["bar2"] == 1.01
  assert isinstance(result["foo"][0]["bar2"], float)

  assert "bar3" in result["foo"][0]
  assert result["foo"][0]["bar3"] == datetime.strptime(input["foo"][0]["bar3"], "%Y-%m-%dT%H:%M:%S%z")
  assert isinstance(result["foo"][0]["bar3"], datetime)

@pytest.mark.asyncio
async def test_when_array_does_not_contain_dict_then_not_converted():
  # Arrange
  input = {
    "foo": [
      "bar1",
      "bar2",
      "bar3"
    ]
  }

  # Act
  result = dict_to_typed_dict(input)

  # Assert
  assert input["foo"][0] == "bar1"
  assert input["foo"][1] == "bar2"
  assert input["foo"][2] == "bar3"

  assert result is not None
  assert "foo" in result

  assert len(result["foo"]) == 3
  
  assert result["foo"][0] == "bar1"
  assert result["foo"][1] == "bar2"
  assert result["foo"][2] == "bar3"
