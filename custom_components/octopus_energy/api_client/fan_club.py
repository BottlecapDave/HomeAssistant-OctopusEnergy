from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


class DiscountPeriod(BaseModel):
    startAt: datetime
    discount: str


class ForecastData(BaseModel):
    validTime: datetime
    projectedDiscount: str


class ForecastInfo(BaseModel):
    baseTime: datetime
    data: List[ForecastData]


class FanClubStatusItem(BaseModel):
    discountSource: str
    current: DiscountPeriod
    historic: List[DiscountPeriod]
    forecast: Optional[ForecastInfo] = None


class FanClubResponse(BaseModel):
    fanClubStatus: List[FanClubStatusItem]
