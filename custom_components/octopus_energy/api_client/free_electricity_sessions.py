from datetime import datetime

from .octoplus_session import BaseOctoplusSession

class FreeElectricitySession(BaseOctoplusSession):
  def __init__(
    self,
    code: str,
    start: datetime,
    end: datetime
  ):
    BaseOctoplusSession.__init__(self, code, start, end)

class FreeElectricitySessionsResponse:
  data: list[FreeElectricitySession]

  def __init__(
    self,
    data: list[FreeElectricitySession]
  ):
    self.data = data
