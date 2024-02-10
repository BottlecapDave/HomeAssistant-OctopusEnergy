from datetime import datetime

class GreennessForecast:
  start: datetime
  end: datetime
  greenness_score: int
  greenness_index: str
  highlight_flag: bool

  def __init__(
    self,
    start: datetime,
    end: datetime,
    greenness_score: int,
    greenness_index: str,
    highlight_flag: bool
  ):
    self.start = start
    self.end = end
    self.greenness_score = greenness_score
    self.greenness_index = greenness_index
    self.highlight_flag = highlight_flag