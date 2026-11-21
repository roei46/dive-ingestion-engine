from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from itertools import islice

import httpx

from dive.schemas.base import EventModel

MAX_THREADS = 10


def fetch_rate(base: str, quote: str) -> float:

    response = httpx.get(
        "http://127.0.0.1:8000/fx", params={"base": base, "quote": quote}, timeout=2.0
    )
    response.raise_for_status()
    data: dict[str, float] = response.json()

    return data["rate"]


def enrich(events: Iterator[EventModel]) -> Iterator[EventModel]:
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as pool:
        while True:
            chunk = list(islice(events, MAX_THREADS))
            if not chunk:
                return
            yield from pool.map(enrich_one, chunk)


def enrich_one(event: EventModel) -> EventModel:
    try:
        event.fx_rate = fetch_rate(event.currency_code(), "EUR")
    except httpx.HTTPError:
        event.fx_fallback = True

    return event
