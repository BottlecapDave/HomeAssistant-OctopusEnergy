import logging

from ..const import (
  CONFIG_COST_NAME,
)

from .cost_tracker_week import OctopusEnergyCostTrackerWeekSensor

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyCostTrackerWeekPeakSensor(OctopusEnergyCostTrackerWeekSensor):
  """Sensor for calculating the cost for a given sensor over the course of a week."""

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_cost_tracker_{self._config[CONFIG_COST_NAME]}_week_peak"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octopus Energy Cost Tracker {self._config[CONFIG_COST_NAME]} Week Peak"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False