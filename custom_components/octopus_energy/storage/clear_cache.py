import logging
import os

from homeassistant.helpers.storage import STORAGE_DIR

_LOGGER = logging.getLogger(__name__)

def clear_cache_files(hass) -> list[str]:
  """Removes all octopus energy cache files from the storage directory. This is executed on a background thread."""
  storage_dir = hass.config.path(STORAGE_DIR)

  cleared_files = []
  if os.path.isdir(storage_dir):
    for filename in os.listdir(storage_dir):
      if filename.startswith("octopus_energy."):
        os.remove(os.path.join(storage_dir, filename))
        cleared_files.append(filename)

  return cleared_files
