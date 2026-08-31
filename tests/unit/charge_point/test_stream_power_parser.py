from custom_components.octopus_energy.utils.charge_point_power_stream import parse_charge_point_power_stream_chunk

def make_part(body: str) -> str:
  return f'Content-Type: application/json\n\n{body}\n'

def test_when_single_complete_reading_chunk_then_reading_parsed():
  # Arrange
  reading_body = '{"payload":{"data":{"electricChargerPowerReadings":{"value":3.2,"unit":"KILOWATT"}}}}'
  chunk = ("--graphql\n" + make_part(reading_body) + "--graphql\n").encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == [{"value": 3.2, "unit": "KILOWATT"}]

def test_when_heartbeat_chunk_then_no_reading_returned():
  # Arrange
  chunk = ("--graphql\n" + make_part("{}") + "--graphql\n").encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == []

def test_when_reading_is_null_then_none_returned_for_that_update():
  # Arrange
  reading_body = '{"payload":{"data":{"electricChargerPowerReadings":null}}}'
  chunk = ("--graphql\n" + make_part(reading_body) + "--graphql\n").encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == [None]

def test_when_chunk_split_across_reads_then_reading_only_parsed_once_boundary_arrives():
  # Arrange
  reading_body = '{"payload":{"data":{"electricChargerPowerReadings":{"value":1.5,"unit":"KILOWATT"}}}}'
  full_part = "--graphql\n" + make_part(reading_body)
  split_point = len(full_part) // 2
  first_half = full_part[:split_point].encode("utf-8")
  second_half = (full_part[split_point:] + "--graphql\n").encode("utf-8")

  # Act
  buffer_after_first, readings_after_first = parse_charge_point_power_stream_chunk("", first_half)
  buffer_after_second, readings_after_second = parse_charge_point_power_stream_chunk(buffer_after_first, second_half)

  # Assert
  assert readings_after_first == []
  assert readings_after_second == [{"value": 1.5, "unit": "KILOWATT"}]

def test_when_multiple_readings_in_one_chunk_then_all_parsed_in_order():
  # Arrange
  first_reading = '{"payload":{"data":{"electricChargerPowerReadings":{"value":1.0,"unit":"KILOWATT"}}}}'
  second_reading = '{"payload":{"data":{"electricChargerPowerReadings":{"value":2.0,"unit":"KILOWATT"}}}}'
  chunk = (
    "--graphql\n" + make_part(first_reading) +
    "--graphql\n" + make_part("{}") +
    "--graphql\n" + make_part(second_reading) +
    "--graphql\n"
  ).encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == [{"value": 1.0, "unit": "KILOWATT"}, {"value": 2.0, "unit": "KILOWATT"}]

def test_when_closing_boundary_marker_then_no_error_and_nothing_parsed():
  # Arrange - "--graphql--" ends up as a bare "--" once already split on "--graphql"
  chunk = "--graphql--".encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == []

def test_when_malformed_json_then_chunk_skipped_without_error():
  # Arrange
  chunk = ("--graphql\n" + make_part("{not valid json") + "--graphql\n").encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == []

def test_when_crlf_line_endings_then_still_parsed_correctly():
  # Arrange
  reading_body = '{"payload":{"data":{"electricChargerPowerReadings":{"value":4.4,"unit":"KILOWATT"}}}}'
  chunk = ("--graphql\r\nContent-Type: application/json\r\n\r\n" + reading_body + "\r\n--graphql\r\n").encode("utf-8")

  # Act
  buffer, readings = parse_charge_point_power_stream_chunk("", chunk)

  # Assert
  assert readings == [{"value": 4.4, "unit": "KILOWATT"}]
