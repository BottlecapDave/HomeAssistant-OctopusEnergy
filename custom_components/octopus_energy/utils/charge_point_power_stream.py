import json

# The multipart boundary used by the charge point live power stream. A fixed
# literal, never guaranteed to land on a chunk edge.
multipart_boundary = "--graphql"

def parse_charge_point_power_stream_chunk(buffer: str, chunk: bytes) -> tuple[str, list]:
  """Feed one more chunk of bytes from the live power multipart stream into the parser.

  Returns a tuple of (new_buffer, readings) where readings is a list of
  parsed values - each either a dict (a real reading, e.g. {"value": ..,
  "unit": ..}) or None (the stream explicitly reported no reading for that
  update). Empty `{}` heartbeat payloads and partial/malformed chunks are
  swallowed and contribute nothing to the returned readings list.

  This is a pure function so the buffering/boundary/JSON-extraction logic
  can be unit tested without a real (or mocked) HTTP connection.
  """
  readings = []

  # Normalise CRLF up front so the boundary/header-body parsing below only
  # ever has to deal with plain \n.
  buffer += chunk.decode("utf-8", errors="ignore").replace("\r\n", "\n")

  # Buffer across reads and only treat a segment as complete once a
  # boundary after it has arrived.
  parts = buffer.split(multipart_boundary)
  buffer = parts.pop()  # last piece may be incomplete - carry it forward

  for raw_part in parts:
    part = raw_part.strip()
    # Empty (the bit before the very first boundary) or the closing
    # "--graphql--" marker (left as bare "--" once already split on
    # "--graphql") - nothing to parse either way.
    if not part or part == "--":
      continue

    body_start = part.find("\n\n")
    body_text = (part[body_start + 2:] if body_start >= 0 else part).strip()
    if not body_text:
      continue

    try:
      payload_data = json.loads(body_text)
    except ValueError:
      continue  # partial/malformed chunk - skip rather than crash the stream

    if not payload_data:
      continue  # {} heartbeat

    reading = None
    if ("payload" in payload_data
        and payload_data["payload"] is not None
        and "data" in payload_data["payload"]
        and payload_data["payload"]["data"] is not None):
      reading = payload_data["payload"]["data"].get("electricChargerPowerReadings")

    readings.append(reading)

  return buffer, readings
