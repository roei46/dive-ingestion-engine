from fastapi import FastAPI, HTTPException

app = FastAPI()
RATES: dict[tuple[str, str], float] = {("ILS", "EUR"): 0.26}


@app.get(
    "/fx",
    summary="Get a fx's result",
    description=("/fx"),
)
def get_fx(base: str, quote: str) -> dict[str, float]:
    rate = RATES.get((base, quote))
    if rate is None:
        raise HTTPException(status_code=404, detail="No rate accepted")

    return {"rate": rate}
