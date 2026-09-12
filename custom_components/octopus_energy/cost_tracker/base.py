from homeassistant.helpers.device import async_entity_id_to_device


def get_cost_tracker_unique_id(tracker_name: str, peak_type = None):
  base_name = f"octopus_energy_cost_tracker_{tracker_name}"
  return f"{base_name}_{peak_type}" if peak_type is not None else base_name


class BaseCostTracker:
  def __init__(self, hass, source_entity_id: str):

    self.device_entry = async_entity_id_to_device(
      hass,
      source_entity_id,
    )