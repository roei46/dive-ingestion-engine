import os
import time
from itertools import islice

from dotenv import load_dotenv

from dive.persistence.db import (
    connection,
    get_cursor,
    save,
    save_signature,
    set_cursor,
    transaction,
)
from dive.pipeline.dlq import DeadLetterQueue
from dive.pipeline.enrich import enrich
from dive.pipeline.pipeline import batcher, parse_json, read_lines, validate
from dive.pipeline.signing import sign_batch

jobs: dict[str, dict[str, int]] = {}
load_dotenv()
key = os.environ["SIGNING_KEY"].encode()

def run_file(path: str, job_id: str) -> dict[str, int]:
    conn = connection(path="data/dive.db")
    cursor = get_cursor(conn, job_id)
    dlq = DeadLetterQueue(connection=conn, job_id=job_id)
    counts: dict[str, int] = {}
    saved = cursor
    lines = read_lines(path=path)
    raw = parse_json(dlq=dlq, lines=lines)
    events = validate(dlq=dlq, dicts=raw)
    sliced_events = islice(events, cursor, None)
    enriched_events = enrich(events=sliced_events)

    batches = batcher(size=500, events=enriched_events)

    batch = next(batches, None)
    while batch is not None:
        start = time.perf_counter()
        with transaction(connection=conn):
            saved += len(batch)
            save(connection=conn, events=batch)
            set_cursor(connection=conn, job_id=job_id, gruop_number=saved)
            records = [event.model_dump(mode="json") for event in batch]
            signature = sign_batch(records, key)
            save_signature(conn, job_id, saved, signature)
            
        elapsed = time.perf_counter() - start

        for event in batch:
            counts[event.version] = counts.get(event.version, 0) + 1
        try:
            batch = batches.send(elapsed)
        except StopIteration:
            batch = None

    conn.commit()
    counts["dlq"] = dlq.count
    jobs[job_id] = counts

    print("counts is: ", counts)
    return counts
