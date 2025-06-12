from homeassistant.core import HomeAssistant

from homeassistant.helpers.entity import generate_entity_id


class OctopusEnergyFanClubSensor:
  _unrecorded_attributes = frozenset({"data_last_retrieved"})

  def __init__(self, hass: HomeAssistant, entity_domain = "sensor"):
    """Init sensor"""

    self.entity_id = generate_entity_id(entity_domain + ".{}", self.unique_id, hass=hass)