import hmac
import os
import time
import zlib

SLOWDOWN = int(os.environ.get("SIGN_SLOWDOWN", "1"))

def canonical_bytes(record: bytes) -> bytes:
    packed = zlib.compress(record)

    return packed


def sign_batch(records: bytes, key: bytes) -> str:
    start = time.perf_counter()
    h = hmac.new(key=key, digestmod="sha256")
    h.update(canonical_bytes(records))
    elapsed = time.perf_counter() - start
    time.sleep(elapsed * (SLOWDOWN - 1))
    
    return h.hexdigest()
