import json
from collections.abc import Generator, Iterator
from typing import Any

from pydantic import ValidationError

from dive.pipeline.dlq import DeadLetterQueue
from dive.schemas.base import EventModel, parse_event

MIN_BATCH = 100
MAX_BATCH = 5000
TARGET_TIME = 0.5


def read_lines(path: str) -> Iterator[str]:
    with open(path, mode="r", errors="replace") as file:
        for line in file:
            yield line.strip()


def parse_json(dlq: DeadLetterQueue, lines: Iterator[str]) -> Iterator[dict[str, Any]]:
    for line in lines:
        try:
            dic = json.loads(line)
            yield dic
        except json.JSONDecodeError as error:
            dlq.add(raw=line, error=str(error))
            continue


def validate(
    dlq: DeadLetterQueue, dicts: Iterator[dict[str, Any]]
) -> Iterator[EventModel]:
    for raw in dicts:
        try:
            event = parse_event(raw=raw)
            yield event
        except (ValueError, ValidationError) as error:
            dlq.add(raw=json.dumps(raw), error=str(error))
            continue


def batcher(
    size: int, events: Iterator[EventModel]
) -> Generator[list[EventModel], float | None, None]:
    batch: list[EventModel] = []

    for event in events:
        batch.append(event)
        if size == len(batch):
            save_time = yield batch
            batch = []
            if save_time is not None:
                if save_time < TARGET_TIME:
                    size = min(MAX_BATCH, size * 2)
                else:
                    size = max(MIN_BATCH, size // 2)

    if batch:
        yield batch