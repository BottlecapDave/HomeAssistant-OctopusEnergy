from datetime import datetime
import logging
from homeassistant.helpers import storage
from homeassistant.util.dt import (parse_datetime)

from ..api_client.intelligent_dispatches import IntelligentDispatches

_LOGGER = logging.getLogger(__name__)

class IntelligentDispatchesHistoryItem:
  timestamp: datetime
  dispatches: IntelligentDispatches

  def __init__(self, timestamp: datetime, dispatches: IntelligentDispatches):
    self.timestamp = timestamp
    self.dispatches = dispatches

  def from_dict(data: dict):
    return IntelligentDispatchesHistoryItem(
      parse_datetime(data["timestamp"]),
      IntelligentDispatches.from_dict(data["dispatches"])
    )
  
  def to_dict(self):
    return {
      "timestamp": self.timestamp,
      "dispatches": self.dispatches.to_dict()
    }

class IntelligentDispatchesHistory:
  history: list[IntelligentDispatchesHistoryItem]

  def __init__(self, history: list[IntelligentDispatchesHistoryItem]):
    self.history = history

  def from_dict(data: dict):
    history = []
    for item in data["history"]:
      history.append(IntelligentDispatchesHistoryItem.from_dict(item))
    
    return IntelligentDispatchesHistory(history)
  
  def to_dict(self):
    return {
      "history": [item.to_dict() for item in self.history]
    }

async def async_load_cached_intelligent_dispatches_history(hass, device_id: str) -> IntelligentDispatchesHistory | None:
  store = storage.Store(hass, "1", f"octopus_energy.intelligent_dispatches_history_{device_id}")

  try:
    data = await store.async_load()
    if data is not None:
      _LOGGER.debug(f"Loaded cached intelligent dispatches history data for {device_id}")
      return IntelligentDispatchesHistory.from_dict(data)
    
    return IntelligentDispatchesHistory([])
  except:
    return IntelligentDispatchesHistory([])
  
async def async_save_cached_intelligent_dispatches_history(hass, device_id: str, intelligent_dispatches_history: IntelligentDispatchesHistory):
  if intelligent_dispatches_history is not None:
    store = storage.Store(hass, "1", f"octopus_energy.intelligent_dispatches_history_{device_id}")
    await store.async_save(intelligent_dispatches_history.to_dict())
    _LOGGER.debug(f"Saved intelligent dispatches history data for ({device_id})")