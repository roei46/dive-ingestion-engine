

import uuid

from fastapi import FastAPI, File, UploadFile

app = FastAPI()

@app.post("/v1/ingest", status_code=202)

async def ingest_file(file: UploadFile) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    result = {"job_id": job_id}

    return  result