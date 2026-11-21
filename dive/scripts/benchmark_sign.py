import json
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import islice, repeat

from dive.pipeline.pipeline import MAX_BATCH
from dive.pipeline.signing import sign_batch

PATH = "data/crash.ndjson"
BATCHES = 16
KEY = b"benchmark-key"  # not the real signing key


def load_batch() -> list[bytes]:
    records: list[bytes] = []
    with open(PATH) as file:
        for line in islice(file, MAX_BATCH):
            try:
                record = json.dumps(json.loads(line), sort_keys=True)
                records.append(record.encode("utf-8"))
            except json.JSONDecodeError:
                continue
    return records


def main() -> None:
    batches = [load_batch()] * BATCHES
    baseline = 0.0
    for workers in (1, 2, 4, 8):
        start = time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            list(pool.map(sign_batch, batches, repeat(KEY)))
        seconds = time.perf_counter() - start
        if workers == 1:
            baseline = seconds
        print(
            f"processes={workers} time={seconds:.2f}s "
            f"speedup={baseline / seconds:.1f}x"
        )


if __name__ == "__main__":
    main()
