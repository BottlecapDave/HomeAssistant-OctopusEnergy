import logging

from .free_electricity_sessions_calendar import OctopusEnergyFreeElectricitySessionsCalendar

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyPowerUpCalendar(OctopusEnergyFreeElectricitySessionsCalendar):
  """Sensor for power up calendar"""

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_{self._account_id}_octoplus_power_up"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Octoplus Power Up ({self._account_id})"

  @property
  def calendar_summary(self):
    """Summary for calendar entries"""
    return f"Octopus Energy Power Up"