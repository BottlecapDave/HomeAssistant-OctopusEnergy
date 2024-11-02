from ..api_client import ApiException, RequestException, ServerException, TimeoutException

def api_exception_to_string(e: ApiException):
  if isinstance(e, ServerException):
    return "Error on Octopus Energy servers. Please try again later."
  if isinstance(e, TimeoutException):
    return "Octopus Energy servers did not respond in a timely manner"
  if isinstance(e, RequestException):
    return f"Octopus Energy server returned one or more errors - {', '.join(e.errors)}"

  return "Error on Octopus Energy servers. Please try again later."