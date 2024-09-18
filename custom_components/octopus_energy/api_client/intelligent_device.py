class IntelligentDevice:
  def __init__(
    self,
    id: str,
    provider: str,
    make:str,
    model: str,
    vehicleBatterySizeInKwh: float | None,
    chargePointPowerInKw: float | None,
    is_charger: bool
  ):
    self.id = id
    self.provider = provider
    self.make = make
    self.model = model
    self.vehicleBatterySizeInKwh = vehicleBatterySizeInKwh
    self.chargePointPowerInKw = chargePointPowerInKw
    self.is_charger = is_charger