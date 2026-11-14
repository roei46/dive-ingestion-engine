from typing import ClassVar, Literal

from pydantic import (
    AwareDatetime,
    BaseModel,
    Field,
)

from dive.common import Currency, Tier
from dive.schemas.base import EventModel


class Carrier(BaseModel):
    id: str
    tier: Tier

class Value(BaseModel):
    amount: float
    currency: Currency

class Route(BaseModel):
    from_: str = Field(alias="from")
    to: str

class ShipmentEventV2(EventModel):
    schema_ver: Literal["v2"] = "v2"
    version: ClassVar[str] = "v2"
    shipment_id: str
    occurred_at: AwareDatetime
    route: Route
    value: Value
    carrier: Carrier
