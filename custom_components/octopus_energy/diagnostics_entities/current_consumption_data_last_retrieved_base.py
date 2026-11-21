from .base import OctopusEnergyBaseDataLastRetrieved

class OctopusEnergyBaseCurrentConsumptionDataLastRetrieved(OctopusEnergyBaseDataLastRetrieved):
  """Base sensor for current consumption data last retrieved, which distinguishes request health from telemetry freshness."""
  _unrecorded_attributes = frozenset({
    *OctopusEnergyBaseDataLastRetrieved._unrecorded_attributes,
    "first_missing_at",
    "latest_reading",
  })

  @property
  def extra_state_attributes(self):
    """Attributes of the sensor."""
    result = self.coordinator.data if self.coordinator is not None else None
    return {
      **(self._attributes if self._attributes is not None else {}),
      "status": getattr(result, "status", None),
      "latest_reading": getattr(result, "latest_reading", None),
      "first_missing_at": getattr(result, "first_missing_at", None),
    }
