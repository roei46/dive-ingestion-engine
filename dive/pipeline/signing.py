import hmac
import zlib


def canonical_bytes(record: bytes) -> bytes:
    packed = zlib.compress(record)

    return packed


def sign_batch(records: bytes, key: bytes) -> str:
    h = hmac.new(key=key, digestmod="sha256")
    h.update(canonical_bytes(records))

    return h.hexdigest()
