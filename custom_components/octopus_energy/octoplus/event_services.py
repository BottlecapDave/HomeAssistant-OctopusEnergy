from homeassistant.core import ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.service import remove_entity_service_fields
from homeassistant.util import slugify

from ..const import DOMAIN

def create_octoplus_event_service_handler(method_name: str, expected_entity_suffix: str):
  """Creates a service handler that raises a helpful error when the targeted entity doesn't support the service"""

  async def async_handle_service(entity, call: ServiceCall):
    method = getattr(entity, method_name, None)
    if method is None:
      account_id = getattr(entity, "_account_id", None)
      raise ServiceValidationError(
        translation_domain=DOMAIN,
        translation_key="octoplus_event_service_unsupported_entity",
        translation_placeholders={
          "entity_id": entity.entity_id,
          "service": f"{DOMAIN}.{call.service}",
          "expected_entity_id": f"event.octopus_energy_{slugify(account_id) if account_id is not None else '{{ACCOUNT_ID}}'}_{expected_entity_suffix}",
        },
      )

    return await method(**remove_entity_service_fields(call))

  return async_handle_service
