from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict

_REGISTRY: dict[str, type["EventModel"]] = {}


class EventModel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    version: ClassVar[str]
    shipment_id: str
    fx_rate: float | None = None
    fx_fallback: bool = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        _REGISTRY[cls.version] = cls

    def currency_code(self) -> str:
        raise NotImplementedError


def parse_event(raw: dict[str, Any]) -> EventModel:
    model = _REGISTRY.get(raw.get("schema_ver", ""))
    if model is None:
        raise ValueError(f"unknown schema_ver: {raw.get('schema_ver')}")

    return model.model_validate(raw)
