from ..api_client import ApiException, RequestException, ServerException, TimeoutException

def api_exception_to_string(e: ApiException):
  if isinstance(e, ServerException):
    return "Error on Octopus Energy servers. Please try again later."
  if isinstance(e, TimeoutException):
    return "Octopus Energy servers did not respond in a timely manner"
  if isinstance(e, RequestException):
    return f"Octopus Energy server returned one or more errors - {', '.join(e.errors)}"

  return "Error on Octopus Energy servers. Please try again later."

def exception_to_string(e: Exception):
  if e is None:
    return 'None'

  if isinstance(e, ApiException):
    return api_exception_to_string(e)
  
  return "Unexpected error. Please review logs fo more information"