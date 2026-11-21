import hmac
import os
import time
import zlib

SLOWDOWN = int(os.environ.get("SIGN_SLOWDOWN", "1"))
# Sizes the CPU work (spec A.3): 20 rounds ≈ 0.5 s per batch of 5,000.
CPU_ROUNDS = int(os.environ.get("SIGN_ROUNDS", "20"))


def canonical_bytes(record: bytes) -> bytes:
    packed = record
    for _ in range(CPU_ROUNDS):
        packed = zlib.compress(record, level=9)

    return packed


def sign_batch(records: list[bytes], key: bytes) -> str:
    start = time.perf_counter()
    h = hmac.new(key=key, digestmod="sha256")
    for record in records:
        h.update(canonical_bytes(record))
    elapsed = time.perf_counter() - start
    time.sleep(elapsed * (SLOWDOWN - 1))
    
    return h.hexdigest()
