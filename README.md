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
