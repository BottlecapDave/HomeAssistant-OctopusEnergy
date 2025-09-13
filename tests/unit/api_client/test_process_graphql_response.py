import pytest
from custom_components.octopus_energy.api_client import AuthenticationException, IntelligentBoostChargeException, RequestException, process_graphql_response

expected_error_message = "This is a custom error"
expected_error_message_2 = "This is another custom error"
expected_error_messages_string = f"{expected_error_message}, {expected_error_message_2}"

def assert_error(errors: list[str]):
  assert errors is not None
  assert len(errors) == 2
  assert errors[0] == expected_error_message
  assert errors[1] == expected_error_message_2

def test_when_process_graphql_response_called_with_no_errors_provided_then_data_is_returned():
  # Arrange
  data = {
    "hello": "world"
  }
  url = "https://api.octopus.energy/graphql"
  request_context = "Test Request"
  ignore_errors = False
  accepted_error_codes = []

  # Act
  result = process_graphql_response(data, url, request_context, ignore_errors, accepted_error_codes)

  # Assert
  assert result == data

@pytest.mark.parametrize("errorCode",["KT-CT-1139", "KT-CT-1111", "KT-CT-1143", "KT-CT-1134", "KT-CT-1135"])
def test_when_process_graphql_response_called_with_authentication_error_code_then_authentication_exception_thrown(errorCode: str):
  # Arrange
  data = {
    "errors": [
      {
        "message": f"{expected_error_message}.",
        "extensions": {
          "errorCode": "KT-CT-0001"
        }
      },
      {
        "message": f"{expected_error_message_2}!",
        "extensions": {
          "errorCode": errorCode
        }
      }
    ]
  }
  url = "https://api.octopus.energy/graphql"
  request_context = "Test Request"
  ignore_errors = False
  accepted_error_codes = []

  # Act
  try:
    process_graphql_response(data, url, request_context, ignore_errors, accepted_error_codes)
    assert False
  except AuthenticationException as ex:
    assert ex.args[0] == f"Authentication failed - {expected_error_messages_string}. See logs for more details."
    assert_error(ex.errors)

def test_when_process_graphql_response_called_with_unknown_error_code_then_request_exception_thrown():
  # Arrange
  data = {
    "errors": [
      {
        "message": f"{expected_error_message}.",
        "extensions": {
          "errorCode": "KT-CT-0001"
        }
      },
      {
        "message": f"{expected_error_message_2}!",
        "extensions": {
          "errorCode": "KT-CT-0002"
        }
      }
    ]
  }
  url = "https://api.octopus.energy/graphql"
  request_context = "Test Request"
  ignore_errors = False
  accepted_error_codes = []

  # Act
  try:
    process_graphql_response(data, url, request_context, ignore_errors, accepted_error_codes)
    assert False
  except RequestException as ex:
    assert ex.args[0] == f"Failed - {expected_error_messages_string}. See logs for more details."
    assert_error(ex.errors)

def test_when_process_graphql_response_called_with_ignore_errors_true_then_data_is_returned():
  # Arrange
  data = {
    "errors": [
      {
        "message": f"{expected_error_message}.",
        "extensions": {
          "errorCode": "KT-CT-0001"
        }
      },
      {
        "message": f"{expected_error_message_2}!",
        "extensions": {
          "errorCode": "KT-CT-0002"
        }
      }
    ]
  }
  url = "https://api.octopus.energy/graphql"
  request_context = "Test Request"
  ignore_errors = True
  accepted_error_codes = []

  # Act
  result = process_graphql_response(data, url, request_context, ignore_errors, accepted_error_codes)

  # Assert
  assert result is not None
  assert result == data

def test_when_process_graphql_response_called_with_accepted_error_code_then_none_is_returned():
  # Arrange
  data = {
    "errors": [
      {
        "message": f"{expected_error_message}.",
        "extensions": {
          "errorCode": "KT-CT-0001"
        }
      },
      {
        "message": f"{expected_error_message_2}!",
        "extensions": {
          "errorCode": "KT-CT-0002"
        }
      }
    ]
  }
  url = "https://api.octopus.energy/graphql"
  request_context = "Test Request"
  ignore_errors = False
  accepted_error_codes = ["KT-CT-0001"]

  # Act
  result = process_graphql_response(data, url, request_context, ignore_errors, accepted_error_codes)

  # Assert
  assert result is None

@pytest.mark.parametrize("boost_charge_refusal_reasons,expected_reason",[
  ("BC_DEVICE_NOT_YET_LIVE", "Device is not yet live"),
  ("BC_DEVICE_RETIRED", "Device is retired"),
  ("BC_DEVICE_SUSPENDED", "Device is suspended"),
  ("BC_DEVICE_DISCONNECTED", "Device is disconnected"),
  ("BC_DEVICE_NOT_AT_HOME", "Device is not at home"),
  ("BC_BOOST_CHARGE_IN_PROGRESS", "Boost charge already in progress"),
  ("BC_DEVICE_FULLY_CHARGED", "Device is already fully charged"),
])
def test_when_process_graphql_response_called_with_boost_charge_refusal_reasons_then_boost_intelligent_exception_thrown(boost_charge_refusal_reasons: str, expected_reason: str):
  # Arrange
  data = {
    "errors": [
      {
        "message": f"{expected_error_message}.",
        "extensions": {
          "errorCode": "KT-CT-0001"
        }
      },
      {
        "message": f"{expected_error_message_2}!",
        "extensions": {
          "errorCode": "KT-CT-0001",
          "boostChargeRefusalReasons": boost_charge_refusal_reasons
        }
      }
    ]
  }
  url = "https://api.octopus.energy/graphql"
  request_context = "Test Request"
  ignore_errors = False
  accepted_error_codes = []

  # Act
  try:
    process_graphql_response(data, url, request_context, ignore_errors, accepted_error_codes)
    assert False
  except IntelligentBoostChargeException as ex:
    assert ex.args[0] == f"Boost failed - {expected_reason} - {expected_error_messages_string}. See logs for more details."
    assert_error(ex.errors)
    assert ex.refusal_reason == expected_reason