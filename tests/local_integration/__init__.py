import logging
import os

logging.getLogger().setLevel(logging.DEBUG)

class TestContext:
  def __init__(self, api_key: str, base_url: str):
    self.api_key = api_key
    self.base_url = base_url

def get_test_context():
  api_key = os.environ["HOME_PRO_API_KEY"]
  if (api_key is None):
      raise Exception("HOME_PRO_API_KEY must be set")

  base_url = os.environ["HOME_PRO_BASE_URL"]
  if (base_url is None):
      raise Exception("HOME_PRO_BASE_URL must be set")
  
  return TestContext(api_key, base_url)