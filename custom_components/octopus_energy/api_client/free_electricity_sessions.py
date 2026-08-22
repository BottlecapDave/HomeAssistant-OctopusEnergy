from datetime import datetime

from .octoplus_session import BaseOctoplusSession

class FreeElectricitySession(BaseOctoplusSession):
  id: str

  def __init__(
    self,
    id: str,
    code: str,
    start: datetime,
    end: datetime
  ):
    BaseOctoplusSession.__init__(self, code, start, end)
    self.id = id

class FreeElectricitySessionsResponse:
  data: list[FreeElectricitySession]

  def __init__(
    self,
    data: list[FreeElectricitySession]
  ):
    self.data = data
