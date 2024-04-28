class IntelligentDevice:
  krakenflexDeviceId: str
  provider: str
  vehicleMake:str
  vehicleModel: str
  vehicleBatterySizeInKwh: float | None
  chargePointMake: str
  chargePointModel: str
  chargePointPowerInKw: float | None

  def __init__(
    self,
    krakenflexDeviceId: str,
    provider: str,
    vehicleMake:str,
    vehicleModel: str,
    vehicleBatterySizeInKwh: float | None,
    chargePointMake: str,
    chargePointModel: str,
    chargePointPowerInKw: float | None
  ):
    self.krakenflexDeviceId = krakenflexDeviceId
    self.provider = provider
    self.vehicleMake = vehicleMake
    self.vehicleModel = vehicleModel
    self.vehicleBatterySizeInKwh = vehicleBatterySizeInKwh
    self.chargePointMake = chargePointMake
    self.chargePointModel = chargePointModel
    self.chargePointPowerInKw = chargePointPowerInKw