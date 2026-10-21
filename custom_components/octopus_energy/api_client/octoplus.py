from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, computed_field


class OctoplusScratchcardSession(BaseModel):
  startsAt: datetime | None = None
  endsAt: datetime | None = None
  externalReference: str | None = None


class OctoplusScratchcardOffer(BaseModel):
  slug: str | None = None
  featureDisplayText: str | None = None


class OctoplusScratchcardPrize(BaseModel):
  typename: str | None = Field(default=None, alias="__typename")

  model_config = ConfigDict(populate_by_name=True)


class OctoplusScratchcard(BaseModel):
  externalReference: str | None = None
  status: str | None = None
  offer: OctoplusScratchcardOffer | None = None
  prize: OctoplusScratchcardPrize | None = None


class OctoplusScratchcardResponse(BaseModel):
  activeSession: OctoplusScratchcardSession | None = None
  scratchcard: OctoplusScratchcard | None = None

  @computed_field
  @property
  def has_active_session(self) -> bool:
    return self.activeSession is not None

  @computed_field
  @property
  def has_scratchcard(self) -> bool:
    return self.scratchcard is not None


class RedeemOctoplusPointsResponse:
  is_successful: bool
  errors: list[str]

  def __init__(
    self,
    is_successful: bool,
    errors: list[str]
  ):
    self.is_successful = is_successful
    self.errors = errors
