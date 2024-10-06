import pytest

from homeassistant.util.dt import (as_utc, parse_datetime)
from custom_components.octopus_energy.config.target_rates import validate_target_rate_config
from custom_components.octopus_energy.const import CONFIG_TARGET_END_TIME, CONFIG_TARGET_HOURS, CONFIG_TARGET_HOURS_MODE, CONFIG_TARGET_HOURS_MODE_EXACT, CONFIG_TARGET_HOURS_MODE_MAXIMUM, CONFIG_TARGET_HOURS_MODE_MINIMUM, CONFIG_TARGET_MAX_RATE, CONFIG_TARGET_MIN_RATE, CONFIG_TARGET_MPAN, CONFIG_TARGET_NAME, CONFIG_TARGET_OFFSET, CONFIG_TARGET_START_TIME, CONFIG_TARGET_TYPE, CONFIG_TARGET_TYPE_CONTINUOUS, CONFIG_TARGET_TYPE_INTERMITTENT, CONFIG_TARGET_WEIGHTING

non_agile_tariff = "E-1R-SUPER-GREEN-24M-21-07-30-C"
agile_tariff = "E-1R-AGILE-FLEX-22-11-25-B"

now = as_utc(parse_datetime("2023-08-20T10:00:00Z"))
mpan = "selected-mpan"

def get_account_info(tariff_code: str = "E-1R-SUPER-GREEN-24M-21-07-30-C", is_active_agreement = True):
  return {
    "electricity_meter_points": [
      {
        "mpan": mpan,
        "agreements": [
          {
            "start": "2023-08-01T00:00:00+01:00" if is_active_agreement else "2023-01-01T00:00:00+01:00",
            "end": "2023-09-01T00:00:00+01:00" if is_active_agreement else "2023-02-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

@pytest.mark.asyncio
async def test_when_config_is_valid_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_RATE: "0",
    CONFIG_TARGET_MAX_RATE: "10",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
async def test_when_optional_config_is_valid_no_errors_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: None,
    CONFIG_TARGET_END_TIME: None,
    CONFIG_TARGET_OFFSET: None,
    CONFIG_TARGET_MIN_RATE: None,
    CONFIG_TARGET_MAX_RATE: None,
    CONFIG_TARGET_WEIGHTING: None,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("name,tariff",[
  ("", non_agile_tariff),
  ("Test", non_agile_tariff),
  ("test@", non_agile_tariff),
  ("", agile_tariff),
  ("Test", agile_tariff),
  ("test@", agile_tariff),
])
async def test_when_config_has_invalid_name_then_errors_returned(name, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: name,
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME in errors
  assert errors[CONFIG_TARGET_NAME] == "invalid_target_name"
  
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("hours,tariff",[
  ("0", non_agile_tariff),
  ("0", agile_tariff),
])
async def test_when_config_has_valid_hours_then_no_errors_returned(hours, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: hours,
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("hours,tariff",[
  ("", non_agile_tariff),
  ("-1.0", non_agile_tariff),
  ("s", non_agile_tariff),
  ("1.01", non_agile_tariff),
  ("1.49", non_agile_tariff),
  ("1.51", non_agile_tariff),
  ("1.99", non_agile_tariff),
  ("", agile_tariff),
  ("-1.0", agile_tariff),
  ("s", agile_tariff),
  ("1.01", agile_tariff),
  ("1.49", agile_tariff),
  ("1.51", agile_tariff),
  ("1.99", agile_tariff),
])
async def test_when_config_has_invalid_hours_then_errors_returned(hours, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: hours,
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_HOURS in errors
  assert errors[CONFIG_TARGET_HOURS] == "invalid_target_hours"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,tariff",[
  ("", non_agile_tariff),
  ("s", non_agile_tariff),
  ("24:00", non_agile_tariff),
  ("-0:01", non_agile_tariff),
  ("00:000", non_agile_tariff),
  ("00:60", non_agile_tariff),
  ("00:00:00", non_agile_tariff),

  ("", agile_tariff),
  ("s", agile_tariff),
  ("24:00", agile_tariff),
  ("-0:01", agile_tariff),
  ("00:000", agile_tariff),
  ("00:60", agile_tariff),
  ("00:00:00", agile_tariff),
])
async def test_when_config_has_invalid_start_time_then_errors_returned(start_time, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: start_time,
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_START_TIME in errors
  assert errors[CONFIG_TARGET_START_TIME] == "invalid_target_time"
  
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("end_time,tariff",[
  ("", non_agile_tariff),
  ("s", non_agile_tariff),
  ("24:00", non_agile_tariff),
  ("-0:01", non_agile_tariff),
  ("00:000", non_agile_tariff),
  ("00:60", non_agile_tariff),
  ("00:00:00", non_agile_tariff),

  ("", agile_tariff),
  ("s", agile_tariff),
  ("24:00", agile_tariff),
  ("-0:01", agile_tariff),
  ("00:000", agile_tariff),
  ("00:60", agile_tariff),
  ("00:00:00", agile_tariff),
])
async def test_when_config_has_invalid_end_time_then_errors_returned(end_time, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: end_time,
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_END_TIME in errors
  assert errors[CONFIG_TARGET_END_TIME] == "invalid_target_time"
  
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("offset,tariff",[
  ("", non_agile_tariff),
  ("s", non_agile_tariff),
  ("00", non_agile_tariff),
  ("-00", non_agile_tariff),
  ("00:00", non_agile_tariff),
  ("-00:00", non_agile_tariff),
  ("24:00:00", non_agile_tariff),
  ("-24:00:00", non_agile_tariff),
  ("00:60:00", non_agile_tariff),
  ("-00:60:00", non_agile_tariff),
  ("00:00:60", non_agile_tariff),
  ("-00:00:60", non_agile_tariff),

  ("", agile_tariff),
  ("s", agile_tariff),
  ("00", agile_tariff),
  ("-00", agile_tariff),
  ("00:00", agile_tariff),
  ("-00:00", agile_tariff),
  ("24:00:00", agile_tariff),
  ("-24:00:00", agile_tariff),
  ("00:60:00", agile_tariff),
  ("-00:60:00", agile_tariff),
  ("00:00:60", agile_tariff),
  ("-00:00:60", agile_tariff),
])
async def test_when_config_has_invalid_offset_then_errors_returned(offset, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: offset,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_OFFSET in errors
  assert errors[CONFIG_TARGET_OFFSET] == "invalid_offset"
  
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time,tariff",[
  ("01:00","02:00", non_agile_tariff),
  ("23:00","00:00", non_agile_tariff),
  ("01:00","02:00", agile_tariff),
  ("23:00","00:00", agile_tariff),
])
async def test_when_hours_exceed_selected_time_frame_then_errors_returned(start_time, end_time, tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: start_time,
    CONFIG_TARGET_END_TIME: end_time,
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }
  account_info = get_account_info(tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_HOURS in errors
  assert errors[CONFIG_TARGET_HOURS] == "invalid_hours_time_frame"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("tariff",[
  (non_agile_tariff),
  (agile_tariff),
])
async def test_when_mpan_not_found_then_errors_returned(tariff):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "16:00",
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }
  account_info = get_account_info(tariff, is_active_agreement=False)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_MPAN in errors
  assert errors[CONFIG_TARGET_MPAN] == "invalid_mpan"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time",[
  ("00:00","00:00"),
  ("15:59","15:59"),
  ("15:59","23:01"),
])
async def test_when_select_mpan_agile_tariff_and_invalid_hours_picked_not_found_then_errors_returned(start_time, end_time):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: start_time,
    CONFIG_TARGET_END_TIME: end_time,
    CONFIG_TARGET_OFFSET: "-00:00:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }
  account_info = get_account_info(agile_tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_END_TIME in errors
  assert errors[CONFIG_TARGET_END_TIME] == "invalid_end_time_agile"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time,offset",[
  ("00:00","00:00","00:00:00"),
  (None, None, None),
])
async def test_when_config_is_valid_and_not_agile_then_no_errors_returned(start_time, end_time, offset):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  if start_time is not None:
    data[CONFIG_TARGET_START_TIME] = start_time

  if end_time is not None:
    data[CONFIG_TARGET_END_TIME] = end_time
  
  if offset is not None:
    data[CONFIG_TARGET_OFFSET] = offset

  account_info = get_account_info(non_agile_tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("start_time,end_time,offset",[
  ("00:00","23:00","00:00:00"),
  ("00:00","16:00","00:00:00"),
  ("23:00","16:00","00:00:00"),
  ("16:00","16:00","00:00:00"),
  ("16:00","00:00","00:00:00"),
  (None, "23:00", None),
  ("16:00", None, None),
  ("10:00","23:00","00:00:00"),
  ("16:30","23:30","00:00:00"),
  ("17:00","14:00","00:00:00"),
])
async def test_when_config_is_valid_and_agile_then_no_errors_returned(start_time, end_time, offset):
  # Arrange
  data = {
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  if start_time is not None:
    data[CONFIG_TARGET_START_TIME] = start_time

  if end_time is not None:
    data[CONFIG_TARGET_END_TIME] = end_time
  
  if offset is not None:
    data[CONFIG_TARGET_OFFSET] = offset

  account_info = get_account_info(agile_tariff)

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("weighting,expected_error",[
  ("*", "invalid_weighting"),
  ("*,*", "invalid_weighting"),
  ("1,*,1,*", "invalid_weighting"),
  ("a,*", "invalid_weighting"),
  ("1,2", "invalid_weighting_slots"),
  ("1,2,3,4", "invalid_weighting_slots"),
])
async def test_when_weighting_is_invalid_then_weighting_error_returned(weighting, expected_error):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_WEIGHTING: weighting,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == expected_error

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("type",[
  (CONFIG_TARGET_TYPE_INTERMITTENT),
])
async def test_when_weighting_set_and_type_invalid_then_weighting_error_returned(type):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: type,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_WEIGHTING: "1,2,3",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_EXACT,
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == "weighting_not_supported_for_type"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("min_rate,max_rate",[
  (None,"1.5"),
  ("1.5",None),
  ("1.5","2.0"),
])
async def test_when_hour_mode_is_minimum_and_minimum_or_maximum_rate_is_specified_then_no_error_returned(min_rate: float, max_rate: float):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_MIN_RATE: min_rate,
    CONFIG_TARGET_MAX_RATE: max_rate,
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
@pytest.mark.parametrize("hour_mode",[
  (CONFIG_TARGET_HOURS_MODE_MINIMUM),
  (CONFIG_TARGET_HOURS_MODE_MAXIMUM),
])
async def test_when_hour_mode_is_not_exact_and_weighting_specified_then_error_returned(hour_mode: str):
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_WEIGHTING: "2,*,2",
    CONFIG_TARGET_MIN_RATE: "0.18",
    CONFIG_TARGET_HOURS_MODE: hour_mode
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_WEIGHTING in errors
  assert errors[CONFIG_TARGET_WEIGHTING] == "weighting_not_supported_for_hour_mode"

  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_HOURS_MODE not in errors

@pytest.mark.asyncio
async def test_when_hour_mode_is_minimum_and_minimum_and_maximum_rate_is_not_specified_then_error_returned():
  # Arrange
  data = {
    CONFIG_TARGET_TYPE: CONFIG_TARGET_TYPE_CONTINUOUS,
    CONFIG_TARGET_NAME: "test",
    CONFIG_TARGET_MPAN: mpan,
    CONFIG_TARGET_HOURS: "1.5",
    CONFIG_TARGET_START_TIME: "00:00",
    CONFIG_TARGET_END_TIME: "00:00",
    CONFIG_TARGET_OFFSET: "-00:30:00",
    CONFIG_TARGET_HOURS_MODE: CONFIG_TARGET_HOURS_MODE_MINIMUM
  }

  account_info = get_account_info()

  # Act
  errors = validate_target_rate_config(data, account_info, now)

  # Assert
  assert CONFIG_TARGET_NAME not in errors
  assert CONFIG_TARGET_MPAN not in errors
  assert CONFIG_TARGET_HOURS not in errors
  assert CONFIG_TARGET_START_TIME not in errors
  assert CONFIG_TARGET_END_TIME not in errors
  assert CONFIG_TARGET_OFFSET not in errors
  assert CONFIG_TARGET_MIN_RATE not in errors
  assert CONFIG_TARGET_MAX_RATE not in errors
  assert CONFIG_TARGET_WEIGHTING not in errors
  assert CONFIG_TARGET_HOURS_MODE in errors
  assert errors[CONFIG_TARGET_HOURS_MODE] == "minimum_or_maximum_rate_not_specified"