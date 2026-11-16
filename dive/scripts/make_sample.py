import json
import random
import sys
from typing import Any

BAD_RATE = 0.005  # 0.5% broken lines (from the PDF, Appendix A.2)


def make_v1(i: int) -> dict[str, Any]:
    return {
        "schema_ver": "v1",
        "shipment_id": f"SHP-{i:08d}",
        "ts": "2026-11-01T09:14:22Z",
        "origin": "IL",
        "dest": "DE",
        "amount": 129.90,
        "currency": "ILS",
        "carrier": "acme",
    }


def make_v2(i: int) -> dict[str, Any]:
    return {
        "schema_ver": "v2",
        "shipment_id": f"SHP-{i:08d}",
        "occurred_at": "2026-11-10T14:02:11Z",
        "route": {"from": "IL", "to": "DE"},
        "value": {"amount": 129.90, "currency": "ILS"},
        "carrier": {"id": "acme", "tier": "gold"},
        "extras": {"partner_field_x": "ignore-me"},
    }


def make_sample(path: str, n: int) -> None:
    with open(path, "w") as f:
        for i in range(n):
            record = make_v1(i) if i % 2 == 0 else make_v2(i)
            if random.random() < BAD_RATE:
                del record["shipment_id"]
            f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    make_sample(sys.argv[1], int(sys.argv[2]))
