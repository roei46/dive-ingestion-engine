

import hmac
import json
import zlib
from typing import Any


def canonical_bytes(record: dict[str, Any]) -> bytes:
    
    text = json.dumps(record, sort_keys=True)  
    raw = text.encode()                     
    packed = zlib.compress(raw)

    return packed


def sign_batch(records: list[dict[str, Any]], key: bytes) -> str:
    h = hmac.new(key=key, digestmod="sha256")  

    for record in records:
        h.update(canonical_bytes(record))

    return h.hexdigest()