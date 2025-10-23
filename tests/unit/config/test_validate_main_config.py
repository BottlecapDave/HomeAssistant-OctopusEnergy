import pytest
import mock

from homeassistant.util.dt import (as_utc, parse_datetime)

from custom_components.octopus_energy.api_client import OctopusEnergyApiClient, RequestException, ServerException, AuthenticationException
from custom_components.octopus_energy.api_client_home_pro import OctopusEnergyHomeProApiClient
from custom_components.octopus_energy.config.main import async_validate_main_config
from custom_components.octopus_energy.const import (
  CONFIG_ACCOUNT_ID,
  CONFIG_MAIN_API_KEY,
  CONFIG_MAIN_HOME_MINI_SETTINGS,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY,
  CONFIG_MAIN_HOME_PRO_SETTINGS,
  CONFIG_MAIN_PRICE_CAP_SETTINGS, 
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP
)
from . import assert_errors_not_present

now = as_utc(parse_datetime("2023-08-20T10:00:00Z"))
mpan = "selected-mpan"

def get_account_info(tariff_code: str = "E-1R-SUPER-GREEN-24M-21-07-30-C"):
  return {
    "electricity_meter_points": [
      {
        "mpan": mpan,
        "agreements": [
          {
            "start": "2023-08-01T00:00:00+01:00",
            "end": "2023-09-01T00:00:00+01:00",
            "tariff_code": tariff_code,
            "product_code": "SUPER-GREEN-24M-21-07-30"
          }
        ]
      }
    ]
  }

config_keys = [
  CONFIG_MAIN_API_KEY, 
  CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION,
  CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES,
  CONFIG_MAIN_CALORIFIC_VALUE,
  CONFIG_MAIN_ELECTRICITY_PRICE_CAP,
  CONFIG_MAIN_GAS_PRICE_CAP,
  CONFIG_MAIN_HOME_PRO_ADDRESS,
  CONFIG_MAIN_HOME_PRO_API_KEY,
]

@pytest.mark.asyncio
async def test_when_data_is_valid_and_minimal_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_CALORIFIC_VALUE: 40
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert_errors_not_present(errors, config_keys)

@pytest.mark.asyncio
async def test_when_data_is_valid_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert_errors_not_present(errors, config_keys)

@pytest.mark.asyncio
async def test_when_account_info_not_found_then_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  async def async_mocked_get_account(*args, **kwargs):
    return None

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_MAIN_API_KEY in errors
    assert errors[CONFIG_MAIN_API_KEY] == "account_not_found"
    
    assert_errors_not_present(errors, config_keys, CONFIG_MAIN_API_KEY)

@pytest.mark.asyncio
async def test_when_account_info_raises_server_error_then_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  async def async_mocked_get_account(*args, **kwargs):
    raise ServerException()

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_MAIN_API_KEY in errors
    assert errors[CONFIG_MAIN_API_KEY] == "server_error"
    
    assert_errors_not_present(errors, config_keys, CONFIG_MAIN_API_KEY)

@pytest.mark.asyncio
async def test_when_account_info_raises_request_error_then_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  async def async_mocked_get_account(*args, **kwargs):
    raise RequestException("blah", [])

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_MAIN_API_KEY in errors
    assert errors[CONFIG_MAIN_API_KEY] == "account_not_found"
    
    assert_errors_not_present(errors, config_keys, CONFIG_MAIN_API_KEY)

@pytest.mark.asyncio
async def test_when_live_electricity_less_than_one_and_supports_live_consumption_is_false_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: False,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 0,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert_errors_not_present(errors, config_keys)

@pytest.mark.asyncio
async def test_when_live_gas_less_than_one_and_supports_live_consumption_is_false_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: False,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 0,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert_errors_not_present(errors, config_keys)

@pytest.mark.asyncio
async def test_when_live_electricity_less_than_one_and_supports_live_consumption_is_true_then_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 0,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_MAIN_HOME_MINI_SETTINGS in errors
    assert CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES in errors[CONFIG_MAIN_HOME_MINI_SETTINGS]
    assert errors[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES] == "value_greater_than_zero"
    
    assert_errors_not_present(errors[CONFIG_MAIN_HOME_MINI_SETTINGS], config_keys, CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES)

@pytest.mark.asyncio
async def test_when_live_gas_less_than_one_and_supports_live_consumption_is_true_then_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 0,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_MAIN_HOME_MINI_SETTINGS in errors
    assert CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES in errors[CONFIG_MAIN_HOME_MINI_SETTINGS]
    assert errors[CONFIG_MAIN_HOME_MINI_SETTINGS][CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES] == "value_greater_than_zero"
    
    assert_errors_not_present(errors[CONFIG_MAIN_HOME_MINI_SETTINGS], config_keys, CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES)

@pytest.mark.asyncio
async def test_when_account_has_been_setup_already_than_one_then_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data, [data[CONFIG_ACCOUNT_ID]])

    # Assert
    assert CONFIG_ACCOUNT_ID in errors
    assert errors[CONFIG_ACCOUNT_ID] == "duplicate_account"
    
    assert_errors_not_present(errors, config_keys, CONFIG_ACCOUNT_ID)

@pytest.mark.asyncio
async def test_when_home_pro_address_is_not_set_and_home_pro_api_key_is_set_then_error_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    },
    CONFIG_MAIN_HOME_PRO_SETTINGS: {
      CONFIG_MAIN_HOME_PRO_API_KEY: "supersecret",
      CONFIG_MAIN_HOME_PRO_ADDRESS: None
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert CONFIG_MAIN_HOME_PRO_SETTINGS in errors
    assert errors[CONFIG_MAIN_HOME_PRO_SETTINGS] == "all_home_pro_values_not_set"

@pytest.mark.asyncio
async def test_when_cannot_connect_to_home_pro_then_error_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    },
    CONFIG_MAIN_HOME_PRO_SETTINGS: {
      CONFIG_MAIN_HOME_PRO_ADDRESS: "http://localhost:8000"
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info
  
  async def async_mocked_ping_home_pro(*args, **kwargs):
    return False

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    with mock.patch.multiple(OctopusEnergyHomeProApiClient, async_ping=async_mocked_ping_home_pro):
      errors = await async_validate_main_config(data)

      # Assert
      assert CONFIG_MAIN_HOME_PRO_SETTINGS in errors
      assert errors[CONFIG_MAIN_HOME_PRO_SETTINGS] == "home_pro_not_responding"

@pytest.mark.asyncio
async def test_when_connect_to_home_pro_throws_authentication_exception_then_error_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    },
    CONFIG_MAIN_HOME_PRO_SETTINGS: {
      CONFIG_MAIN_HOME_PRO_ADDRESS: "http://localhost:8000"
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info
  
  async def async_mocked_ping_home_pro(*args, **kwargs):
    raise AuthenticationException("cannot connect", [])

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    with mock.patch.multiple(OctopusEnergyHomeProApiClient, async_ping=async_mocked_ping_home_pro):
      errors = await async_validate_main_config(data)

      # Assert
      assert CONFIG_MAIN_HOME_PRO_SETTINGS in errors
      assert errors[CONFIG_MAIN_HOME_PRO_SETTINGS] == "home_pro_authentication_failed"

@pytest.mark.asyncio
async def test_when_connect_to_home_pro_throws_general_exception_then_error_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    },
    CONFIG_MAIN_HOME_PRO_SETTINGS: {
      CONFIG_MAIN_HOME_PRO_ADDRESS: "http://localhost:8000"
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info
  
  async def async_mocked_ping_home_pro(*args, **kwargs):
    raise SystemError("cannot connect")

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    with mock.patch.multiple(OctopusEnergyHomeProApiClient, async_ping=async_mocked_ping_home_pro):
      errors = await async_validate_main_config(data)

      # Assert
      assert CONFIG_MAIN_HOME_PRO_SETTINGS in errors
      assert errors[CONFIG_MAIN_HOME_PRO_SETTINGS] == "home_pro_connection_failed"

@pytest.mark.asyncio
async def test_when_can_connect_to_home_pro_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {
      CONFIG_MAIN_SUPPORTS_LIVE_CONSUMPTION: True,
      CONFIG_MAIN_LIVE_ELECTRICITY_CONSUMPTION_REFRESH_IN_MINUTES: 1,
      CONFIG_MAIN_LIVE_GAS_CONSUMPTION_REFRESH_IN_MINUTES: 1,
    },
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {
      CONFIG_MAIN_ELECTRICITY_PRICE_CAP: 38.5,
      CONFIG_MAIN_GAS_PRICE_CAP: 10.5,
    },
    CONFIG_MAIN_HOME_PRO_SETTINGS: {
      CONFIG_MAIN_HOME_PRO_ADDRESS: "http://localhost:8000"
    }
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info
  
  async def async_mocked_ping_home_pro(*args, **kwargs):
    return True

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    with mock.patch.multiple(OctopusEnergyHomeProApiClient, async_ping=async_mocked_ping_home_pro):
      errors = await async_validate_main_config(data)

      # Assert
      assert_errors_not_present(errors, config_keys)

@pytest.mark.asyncio
async def test_when_objects_are_empty_then_no_errors_returned():
  # Arrange
  data = {
    CONFIG_MAIN_API_KEY: "test-api-key",
    CONFIG_ACCOUNT_ID: "A-123",
    CONFIG_MAIN_HOME_MINI_SETTINGS: {},
    CONFIG_MAIN_CALORIFIC_VALUE: 40,
    CONFIG_MAIN_PRICE_CAP_SETTINGS: {},
    CONFIG_MAIN_HOME_PRO_SETTINGS: {}
  }

  account_info = get_account_info()
  async def async_mocked_get_account(*args, **kwargs):
    return account_info
  
  async def async_mocked_ping_home_pro(*args, **kwargs):
    return True

  # Act
  with mock.patch.multiple(OctopusEnergyApiClient, async_get_account=async_mocked_get_account):
    errors = await async_validate_main_config(data)

    # Assert
    assert_errors_not_present(errors, config_keys)