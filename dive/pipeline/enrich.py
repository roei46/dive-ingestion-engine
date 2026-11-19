from collections.abc import Iterator

import httpx

from dive.schemas.base import EventModel


def fetch_rate(base: str, quote: str) -> float:

    response = httpx.get("http://127.0.0.1:8000/fx", params={"base": base, "quote": quote}, timeout=2.0)
    response.raise_for_status()
    data: dict[str, float] = response.json()

    return data["rate"]

def enrich(events: Iterator[EventModel]) -> Iterator[EventModel]:
    for event in events:
        try:
            event.fx_rate = fetch_rate(event.currency_code(), "EUR")
        except httpx.HTTPError:
            event.fx_fallback = True

        yield event