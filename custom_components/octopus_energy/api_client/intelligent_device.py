class IntelligentDevice:
  def __init__(
    self,
    id: str,
    provider: str,
    make:str,
    model: str,
    vehicleBatterySizeInKwh: float | None,
    chargePointPowerInKw: float | None,
    device_type: str,
    is_charger: bool
  ):
    self.id = id
    self.provider = provider
    self.make = make
    self.model = model
    self.vehicleBatterySizeInKwh = vehicleBatterySizeInKwh
    self.chargePointPowerInKw = chargePointPowerInKw
    self.device_type = device_type
    self.is_charger = is_charger

  def to_dict(self):
    return {
      "id": self.id,
      "provider": self.provider,
      "make": self.make,
      "model": self.model,
      "vehicleBatterySizeInKwh": self.vehicleBatterySizeInKwh,
      "chargePointPowerInKw": self.chargePointPowerInKw,
      "device_type": self.device_type,
      "is_charger": self.is_charger,
    }