from datetime import datetime, timezone
import json
import aiohttp
import logging
from threading import RLock

from ..api_client import AuthenticationException, RequestException, ServerException, TimeoutException

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHomeProApiClient:
  _session_lock = RLock()

  def __init__(self, base_url: str, api_key: str, timeout_in_seconds = 20):
    if (base_url is None):
      raise Exception('BaseUrl is not set')

    self._api_key = api_key
    self._base_url = base_url

    self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_in_seconds, sock_read=timeout_in_seconds)
    self._default_headers = {}

    self._session = None

  def has_api_key(self):
    return self._api_key is not None

  async def async_close(self):
    with self._session_lock:
      if self._session is not None:
        await self._session.close()

  def _create_client_session(self):
    if self._session is not None:
      return self._session
    
    with self._session_lock:
      self._session = aiohttp.ClientSession(timeout=self._timeout, headers=self._default_headers)
      return self._session
    
  async def async_ping(self):
    try:
      client = self._create_client_session()
      url = f'{self._base_url}:3000/get_meter_consumption'
      data = { "meter_type": "elec" }
      async with client.post(url, json=data) as response:
        response_body = await self.__async_read_response__(response, url)
        if (response_body is not None and "Status" in response_body):
          status: str = response_body["Status"]
          return status.lower() == "success"
      
      return False
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()

  async def async_get_consumption(self, is_electricity: bool) -> list | None:
    """Get the latest consumption"""

    try:
      client = self._create_client_session()
      meter_type = 'elec' if is_electricity else 'gas'
      url = f'{self._base_url}:3000/get_meter_consumption'
      data = { "meter_type": meter_type }
      async with client.post(url, json=data) as response:
        response_body = await self.__async_read_response__(response, url)
        if (response_body is not None and "meter_consump" in response_body):
          meter_consump = json.loads(response_body["meter_consump"])
          if "consum" in meter_consump:
            data = meter_consump["consum"]
            divisor = int(data["raw"]["divisor"], 16)
            return [{
              "total_consumption": int(data["consumption"]) / divisor if divisor > 0 else None,
              # Base divisor is 1000, but reports of it being 10000 which represent a factor of 10 out in the reported value. Therefore we are using
              # 1000 as our baseline for our divisor so our demand is still reported in watts https://forum.octopus.energy/t/for-the-pro-user/8453/2892
              "demand": float(data["instdmand"]) / (divisor / 1000) if divisor > 0 and "instdmand" in data else None,
              "start": datetime.fromtimestamp(int(meter_consump["time"]), timezone.utc),
              "end": datetime.fromtimestamp(int(meter_consump["time"]), timezone.utc),
              "is_kwh": data["unit"] == 0
            }]
        
        return None
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def async_set_screen(self, value: str, animation_type: str, type: str, brightness: int, animation_interval: int):
    """Get the latest consumption"""

    if self._api_key is None:
      raise Exception('API key is not set, so screen cannot be contacted')

    try:
      client = self._create_client_session()
      url = f'{self._base_url}:8000/screen'
      headers = { "Authorization": self._api_key }
      payload = {
        # API doesn't support none or empty string as a valid value
        "value": f"{value}" if value is not None and value != "" else " ",
        "animationType": f"{animation_type}",
        "type": f"{type}",
        "brightness": brightness,
        "animationInterval": animation_interval
      }

      async with client.post(url, json=payload, headers=headers) as response:
        await self.__async_read_response__(response, url)
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def __async_read_response__(self, response, url):
    """Reads the response, logging any json errors"""

    text = await response.text()
    _LOGGER.debug(f"response: {text}")

    if response.status >= 400:
      if response.status >= 500:
        msg = f'DO NOT REPORT - Octopus Energy server error ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise ServerException(msg)
      elif response.status in [401, 403]:
        msg = f'Failed to send request ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise AuthenticationException(msg, [])
      elif response.status not in [404]:
        msg = f'Failed to send request ({url}): {response.status}; {text}'
        _LOGGER.warning(msg)
        raise RequestException(msg, [])
      
      _LOGGER.info(f"Response {response.status} for '{url}' receivedL {text}")
      return None

    data_as_json = None
    try:
      if text is not None and text != "":
        data_as_json = json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
    
    return data_as_json
