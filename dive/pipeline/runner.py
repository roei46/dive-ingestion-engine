import json
import os
import sqlite3
import time
from concurrent.futures import Future, ProcessPoolExecutor
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
from dive.schemas.base import EventModel

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
    in_flight: list[tuple[list[EventModel], int, Future[str]]] = []

    batch = next(batches, None)
    with ProcessPoolExecutor(max_workers=4) as pool:
        while batch is not None:
            start = time.perf_counter()
            saved += len(batch)
            records: bytes = json.dumps(
               [event.model_dump(mode="json") for event in batch]
            ).encode("utf-8")
            future = pool.submit(sign_batch, records, key)
            in_flight.append((batch, saved, future))
            if len(in_flight) == 4:
                in_flight_oldest_item = in_flight.pop(0)
                old_batch, old_cursor, old_future = in_flight_oldest_item

                save_batch(
                    conn=conn,
                    batch=old_batch,
                    job_id=job_id,
                    end_cursor=old_cursor,
                    signature=old_future.result(),
                )

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

    for old_batch, old_cursor, old_future in in_flight:
        save_batch(
            conn=conn,
            batch=old_batch,
            job_id=job_id,
            end_cursor=old_cursor,
            signature=old_future.result(),
        )

    print("counts is: ", counts)
    return counts


def save_batch(
    conn: sqlite3.Connection,
    job_id: str,
    batch: list[EventModel],
    end_cursor: int,
    signature: str,
) -> None:
    with transaction(connection=conn):
        save(connection=conn, events=batch)
        set_cursor(connection=conn, job_id=job_id, gruop_number=end_cursor)
        save_signature(
            connection=conn,
            job_id=job_id,
            end_cursor=end_cursor,
            signature=signature,
        )
