from datetime import datetime
import json
import aiohttp
import logging
from threading import RLock

from ..api_client import AuthenticationException, RequestException, ServerException, TimeoutException

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyHomeProApiClient:
  _session_lock = RLock()

  def __init__(self, base_url: str, api_key: str, timeout_in_seconds = 20):
    if (api_key is None):
      raise Exception('API KEY is not set')
    
    if (base_url is None):
      raise Exception('BaseUrl is not set')

    self._api_key = api_key
    self._base_url = base_url

    self._timeout = aiohttp.ClientTimeout(total=None, sock_connect=timeout_in_seconds, sock_read=timeout_in_seconds)
    self._default_headers = {}

    self._session = None

  async def async_close(self):
    with self._session_lock:
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
      url = f'{self._base_url}/get_meter_info?meter_type=elec'
      headers = { "Authorization": self._api_key }
      async with client.get(url, headers=headers) as response:
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
      url = f'{self._base_url}/get_meter_consumption?meter_type={meter_type}'
      headers = { "Authorization": self._api_key }
      async with client.get(url, headers=headers) as response:
        response_body = await self.__async_read_response__(response, url)
        if (response_body is not None and "meter_consump" in response_body and "consum" in response_body["meter_consump"]):
          data = response_body["meter_consump"]["consum"]
          return [{
            "total_consumption": int(data["consumption"]) / 1000,
            "demand": int(data["instdmand"]) if "instdmand" in data else 0,
            "start": datetime.utcfromtimestamp(int(response_body["meter_consump"]["time"])),
            "end": datetime.utcfromtimestamp(int(response_body["meter_consump"]["time"]))
          }]
        
        return None
    
    except TimeoutError:
      _LOGGER.warning(f'Failed to connect. Timeout of {self._timeout} exceeded.')
      raise TimeoutException()
    
  async def __async_read_response__(self, response, url):
    """Reads the response, logging any json errors"""

    text = await response.text()

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
      
      _LOGGER.info(f"Response {response.status} for '{url}' received")
      return None

    data_as_json = None
    try:
      data_as_json = json.loads(text)
    except:
      raise Exception(f'Failed to extract response json: {url}; {text}')
    
    return data_as_json