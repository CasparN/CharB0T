# -*- coding: utf-8 -*-
import datetime
from typing import TypedDict


class BannerStatus(TypedDict):
    """Basic banner status"""

    user_id: int
    quote: str
    color: str | None
    gradient: bool
    cooldown: datetime.datetime
    approved: bool


class BannerStatusPoints(BannerStatus):
    """Banner status, but with user's points included"""

    points: int
