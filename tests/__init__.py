import os

def get_test_context():
  api_key = os.environ["API_KEY"]
  if (api_key == None):
      raise Exception("API_KEY must be set")

  gas_mprn = os.environ["GAS_MPRN"]
  if (gas_mprn == None):
      raise Exception("GAS_MPRN must be set")

  gas_serial_number = os.environ["GAS_SN"]
  if (gas_serial_number == None):
      raise Exception("GAS_SN must be set")

  return {
    "api_key": api_key,
    "gas_mprn": gas_mprn,
    "gas_serial_number": gas_serial_number
  }