# DIVE

## Memory bound (in-flight work)

The signing stage keeps at most `MAX_IN_FLIGHT` batches in flight
(`dive/pipeline/runner.py`). When the window is full, the runner waits for
the oldest batch before it reads the next one. So a slow CPU stage slows
the reader instead of filling memory.

**RAM held by in-flight work ≤ MAX_IN_FLIGHT × batch footprint**

| Value           | Number                            | Where                       |
|-----------------|-----------------------------------|-----------------------------|
| MAX_IN_FLIGHT   | 4                                 | `dive/pipeline/runner.py`   |
| Largest batch   | 5,000 events (`MAX_BATCH`)        | `dive/pipeline/pipeline.py` |
| Batch footprint | 11.6 MB (10.4 models + 1.2 bytes) | measured                    |
| **Bound**       | **4 × 11.6 MB ≈ 46 MB**           |                             |

The bound does not depend on file size. The task limit is 512 MB.

Measured with:

    poetry run python -m dive.scripts.measure_batch

## CPU stage: signature chain + benchmark

Each batch is signed in a `ProcessPoolExecutor` (`dive/pipeline/signing.py`),
as in spec A.3: one HMAC-SHA256 per batch, updated record by record with
`canonical_bytes(record)` (sorted-key JSON + zlib). The runner sends each
record as `bytes` (no Pydantic models cross the process boundary).

`CPU_ROUNDS = 20` sizes the work so the stage is CPU-bound: about 0.5 s per
batch of 5,000 records (one plain compression pass was only ~25 ms).

Benchmark: 16 batches of 5,000 records, on a 14-core Mac:

| Processes | Time   | Speedup |
|-----------|--------|---------|
| 1         | 7.69 s | 1.0x    |
| 2         | 4.05 s | 1.9x    |
| 4         | 2.22 s | 3.5x    |
| 8         | 1.20 s | 6.4x    |

    poetry run python -m dive.scripts.benchmark_sign

## Enrichment rate limit

Enrichment calls the FX API from a `ThreadPoolExecutor(max_workers=MAX_THREADS)`
(`dive/pipeline/enrich.py`, `MAX_THREADS = 10`). The pool size is the limit:
at most 10 requests are open to the FX API at the same time.

We chose threads over `asyncio.TaskGroup` + `Semaphore` because the calls are
blocking `httpx` calls and the rest of the pipeline is plain generators.
Threads keep it simple, and the GIL is released while a thread waits on the
network.
