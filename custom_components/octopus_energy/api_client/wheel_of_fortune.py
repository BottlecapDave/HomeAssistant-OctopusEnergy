class WheelOfFortuneSpinsResponse:
  electricity: int | None
  gas: int | None

  def __init__(
    self,
    electricity: int | None,
    gas: int | None
  ):
    self.electricity = electricity
    self.gas = gas


def build_wheel_of_fortune_query(
  account_id: str,
  include_electricity: bool = True,
  include_gas: bool = True,
) -> str:
  """Build a query containing only the supplies being monitored."""
  fields = []

  if include_electricity:
    fields.append(f'''electricity: wheelOfFortuneSpinsAllowed(fuelType:ELECTRICITY, accountNumber: "{account_id}") {{
    spinsAllowed
  }}''')

  if include_gas:
    fields.append(f'''gas: wheelOfFortuneSpinsAllowed(fuelType:GAS, accountNumber: "{account_id}") {{
    spinsAllowed
  }}''')

  if len(fields) == 0:
    raise ValueError("At least one supply must be included")

  return "query {\n  " + "\n  ".join(fields) + "\n}"


def map_wheel_of_fortune_spins_response(
  response_body: dict | None,
  include_electricity: bool = True,
  include_gas: bool = True,
) -> WheelOfFortuneSpinsResponse | None:
  """Map a response while allowing excluded supplies to be absent."""
  if response_body is None or "data" not in response_body or isinstance(response_body["data"], dict) == False:
    return None

  spins = response_body["data"]
  if ((include_electricity and "electricity" not in spins) or
      (include_gas and "gas" not in spins)):
    return None

  electricity = None
  if include_electricity:
    electricity_data = spins["electricity"]
    electricity = int(electricity_data["spinsAllowed"]) if electricity_data is not None and "spinsAllowed" in electricity_data else 0

  gas = None
  if include_gas:
    gas_data = spins["gas"]
    gas = int(gas_data["spinsAllowed"]) if gas_data is not None and "spinsAllowed" in gas_data else 0

  return WheelOfFortuneSpinsResponse(electricity, gas)
