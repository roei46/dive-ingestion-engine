from typing import ClassVar, Literal

from pydantic import (
    AwareDatetime,
)

from dive.common import Currency
from dive.schemas.base import EventModel


class ShipmentEventV1(EventModel):
    schema_ver: Literal["v1"] = "v1"
    version: ClassVar[str] = "v1"
    shipment_id: str
    ts: AwareDatetime
    origin: str
    dest: str
    amount: float
    currency: Currency
    carrier: str

    def currency_code(self) -> str:
        return self.currency
