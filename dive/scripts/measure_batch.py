import json
import tracemalloc
from itertools import islice

from dive.pipeline.pipeline import MAX_BATCH
from dive.schemas.base import EventModel, parse_event

PATH = "data/crash.ndjson"
MB = 1_000_000


def main() -> None:
    tracemalloc.start()

    events: list[EventModel] = []
    with open(PATH) as file:
        for line in islice(file, MAX_BATCH):
            try:
                events.append(parse_event(raw=json.loads(line)))
            except ValueError:
                continue
    models_memory, _ = tracemalloc.get_traced_memory()

    records = json.dumps(
        [event.model_dump(mode="json") for event in events]
    ).encode("utf-8")
    total_memory, _ = tracemalloc.get_traced_memory()

    print("events:", len(events))
    print("models:", round(models_memory / MB, 1), "MB")
    print("bytes: ", round(len(records) / MB, 1), "MB")
    print("batch footprint:", round(total_memory / MB, 1), "MB")


if __name__ == "__main__":
    main()
