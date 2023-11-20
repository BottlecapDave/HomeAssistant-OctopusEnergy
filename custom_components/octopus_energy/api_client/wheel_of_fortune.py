class WheelOfFortuneSpinsResponse:
  electricity: int
  gas: int

  def __init__(
    self,
    electricity: int,
    gas: int
  ):
    self.electricity = electricity
    self.gas = gas