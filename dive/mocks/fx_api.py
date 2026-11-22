import os
import threading

from fastapi import FastAPI, HTTPException

app = FastAPI()
RATES: dict[tuple[str, str], float] = {("ILS", "EUR"): 0.26}
FAIL_MODE = str(os.environ.get("FAIL_MODE", "none"))
FAIL_AFTER = int(os.environ.get("FAIL_AFTER", "3"))
HANG = threading.Event()
calls = 0

@app.get(
    "/fx",
    summary="Get a fx's result",
    description=("/fx"),
)
def get_fx(base: str, quote: str) -> dict[str, float]:
    global calls
    calls += 1
    
    rate = RATES.get((base, quote))

    if FAIL_MODE == "hang" and calls > FAIL_AFTER:
        HANG.wait()

    if FAIL_MODE == "error" and calls > FAIL_AFTER:
        raise HTTPException(status_code=500, detail="error")

    if FAIL_MODE == "rate_limit" and calls > FAIL_AFTER:
        raise HTTPException(status_code=429, detail="too many requests")
    
    if rate is None:
        raise HTTPException(status_code=404, detail="No rate accepted")

    return {"rate": rate}
