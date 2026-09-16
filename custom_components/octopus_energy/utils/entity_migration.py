import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from ..const import DOMAIN

_LOGGER = logging.getLogger(__name__)

def async_migrate_unique_ids(hass: HomeAssistant, platform: str, migrations: list[dict]):
  """One-off migration of unique_id (and its derived entity_id) for entities
  that changed shape. `migrations` is a list of {"old": ..., "new": ...}
  unique_id pairs. new_unique_id is slugified the same way
  generate_entity_id() does internally, so the resulting entity_id is always
  valid - a raw f-string + .lower() does NOT do this (unique_ids containing a
  hyphenated UUID would build an invalid entity_id and silently fail to
  migrate).

  Temporary: delete this call/helper once deployed (see PR #1854 review).
  """
  registry = er.async_get(hass)
  for item in migrations:
    entity_id = registry.async_get_entity_id(platform, DOMAIN, item["old"])
    if entity_id is not None:
      try:
        registry.async_update_entity(entity_id, new_entity_id=f'{platform}.{slugify(item["new"])}', new_unique_id=item["new"])
        _LOGGER.info(f'Migrated entity id and unique id for {item["old"]} to {item["new"]}')
      except Exception as e:
        _LOGGER.warning(f'Failed to migrate entity id and unique id for {item["old"]} to {item["new"]} - {e}')
