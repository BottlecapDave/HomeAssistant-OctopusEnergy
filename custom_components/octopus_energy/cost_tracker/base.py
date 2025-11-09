from homeassistant.helpers.device import async_entity_id_to_device

class BaseCostTracker:
  def __init__(self, hass, source_entity_id: str):

    self.device_entry = async_entity_id_to_device(
      hass,
      source_entity_id,
    )