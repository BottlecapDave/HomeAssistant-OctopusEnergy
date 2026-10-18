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

  def to_dict(self):
    return {
      "starts_at": self.activeSession.startsAt if self.activeSession is not None else None,
      "ends_at": self.activeSession.endsAt if self.activeSession is not None else None,
      "session_external_reference": self.activeSession.externalReference if self.activeSession is not None else None,
      "scratchcard_external_reference": self.scratchcard.externalReference if self.scratchcard is not None else None,
      "scratchcard_status": self.scratchcard.status if self.scratchcard is not None else None,
      "offer_slug": (
        self.scratchcard.offer.slug
        if self.scratchcard is not None and self.scratchcard.offer is not None
        else None
      ),
      "feature_display_text": (
        self.scratchcard.offer.featureDisplayText
        if self.scratchcard is not None and self.scratchcard.offer is not None
        else None
      ),
      "prize_type": (
        self.scratchcard.prize.typename
        if self.scratchcard is not None and self.scratchcard.prize is not None
        else None
      ),
    }


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
