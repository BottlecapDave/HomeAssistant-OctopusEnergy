from datetime import datetime

class GreennessForecast:
  start: datetime
  end: datetime
  greennessScore: int
  greennessIndex: str
  highlightFlag: bool

  def __init__(
    self,
    start: datetime,
    end: datetime,
    greennessScore: int,
    greennessIndex: str,
    highlightFlag: bool
  ):
    self.start = start
    self.end = end
    self.greennessScore = greennessScore
    self.greennessIndex = greennessIndex
    self.highlightFlag = highlightFlag