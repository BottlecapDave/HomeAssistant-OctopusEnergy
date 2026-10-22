from datetime import datetime

from homeassistant.util.dt import (as_utc, parse_datetime)

class ChargePackDevice:
  """A home battery Octopus controls through SmartFlex (a Charge Pack): Octopus
  plans when it charges and discharges. Found by its device type (INVERTERS)."""

  def __init__(self, id: str, name: str | None, provider: str | None, device_type: str, status: str | None = None,
               make: str | None = None, model: str | None = None):
    self.id = id
    self.name = name
    self.provider = provider
    self.device_type = device_type
    self.status = status
    self._make = make
    self._model = model

  @property
  def make(self) -> str | None:
    """From the API (SmartFlexInverter), else the first word of its name, e.g. "Sigenergy"."""
    if self._make:
      return self._make
    return self.name.split(" ", 1)[0] if self.name else None

  @property
  def model(self) -> str | None:
    """From the API, else the rest of its name, e.g. "SigenStor EC 12.0 SP"."""
    if self._model:
      return self._model
    parts = self.name.split(" ", 1) if self.name else []
    return parts[1] if len(parts) > 1 else self.name

  def to_dict(self):
    return {
      "id": self.id,
      "name": self.name,
      "provider": self.provider,
      "device_type": self.device_type,
      "status": self.status,
      "make": self._make,
      "model": self._model,
    }

  def from_dict(data: dict):
    return ChargePackDevice(data["id"], data.get("name"), data.get("provider"), data.get("device_type"), data.get("status"),
                            data.get("make"), data.get("model"))

class ChargePackStatus:
  """What Octopus says about the battery: current (e.g. LIVE), current_state (e.g.
  SMART_CONTROL_CAPABLE) and whether smart control is suspended."""

  def __init__(self, current: str | None, current_state: str | None, is_suspended: bool | None):
    self.current = current
    self.current_state = current_state
    self.is_suspended = is_suspended

  def __eq__(self, other):
    return (isinstance(other, ChargePackStatus) and self.current == other.current
            and self.current_state == other.current_state and self.is_suspended == other.is_suspended)

class ChargePackDispatches:
  """One read: the planned dispatches and the battery's status (None if it wasn't returned)."""

  def __init__(self, planned: list, status: ChargePackStatus | None):
    self.planned = planned
    self.status = status

class ChargePackDispatch:
  """A planned charge or discharge. Octopus gives a charge a negative
  energyAddedKwh and a discharge a positive one (0: idle)."""

  def __init__(self, start: datetime, end: datetime, energy_added_kwh: float | None, type: str | None = None):
    self.start = start
    self.end = end
    self.energy_added_kwh = energy_added_kwh
    self.type = type

  @property
  def kind(self) -> str:
    """"charge", "discharge" or "idle"."""
    kwh = self.energy_added_kwh or 0
    return "charge" if kwh < 0 else "discharge" if kwh > 0 else "idle"

  @property
  def kwh(self) -> float:
    """The energy, either way."""
    return abs(self.energy_added_kwh or 0)

  def __eq__(self, other):
    return (isinstance(other, ChargePackDispatch) and self.start == other.start and self.end == other.end
            and self.energy_added_kwh == other.energy_added_kwh and self.type == other.type)

  def __repr__(self):
    return f"ChargePackDispatch({self.start.isoformat()}, {self.end.isoformat()}, {self.energy_added_kwh}, {self.type})"

  def to_dict(self):
    return {
      "start": self.start.isoformat(),
      "end": self.end.isoformat(),
      "energy_added_kwh": self.energy_added_kwh,
      "type": self.type,
    }

  def from_dict(data: dict):
    return ChargePackDispatch(
      as_utc(parse_datetime(data["start"])),
      as_utc(parse_datetime(data["end"])),
      float(data["energy_added_kwh"]) if data.get("energy_added_kwh") is not None else None,
      data.get("type")
    )
