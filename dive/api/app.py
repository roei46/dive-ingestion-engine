import tempfile
import uuid
from contextlib import closing
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from starlette.datastructures import UploadFile

from dive.persistence.db import (
    DB_PATH,
    connection,
    count_dead_letters,
    get_cursor,
    get_job_file,
    list_dead_letters,
    save_job_file,
    transaction,
)
from dive.pipeline.runner import jobs, run_file

app = FastAPI()

CHUNK_SIZE = 1024 * 1024  # 1 MB


class ResumeResponse(BaseModel):
    job_id: str
    resume_from: int


class DeadLetterItem(BaseModel):
    raw: str
    error: str


class DeadLetterPage(BaseModel):
    job_id: str
    total: int
    limit: int
    offset: int
    items: list[DeadLetterItem]


@app.post(
    "/v1/ingest",
    status_code=202,
    summary="Upload an NDJSON file for ingestion",
    description=(
        "Accepts NDJSON (one JSON event per line, schema v1 or v2) in either of two "
        "ways: a multipart upload with a `file` field, or a raw request body with "
        "`Content-Type: application/x-ndjson`. The data is copied to a temporary "
        "file in 1 MB chunks, so it is never held in memory as a whole. Returns 202 "
        "with a `job_id` right away; processing runs in the background. Poll "
        "`GET /v1/jobs/{job_id}` for the result."
    ),
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "multipart/form-data": {
                    "schema": {
                        "type": "object",
                        "properties": {"file": {"type": "string", "format": "binary"}},
                        "required": ["file"],
                    }
                },
                "application/x-ndjson": {
                    "schema": {"type": "string", "format": "binary"}
                },
            },
        }
    },
)
async def ingest_file(
    request: Request, background_task: BackgroundTasks
) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    content_type = request.headers.get("content-type", "")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ndjson") as target:
        if content_type.startswith("multipart/form-data"):
            form = await request.form()
            upload = form.get("file")
            if not isinstance(upload, UploadFile):
                raise HTTPException(status_code=422, detail="Missing 'file' field")
            while True:
                piece = await upload.read(CHUNK_SIZE)
                if not piece:
                    break
                target.write(piece)
        elif content_type.startswith("application/x-ndjson"):
            async for piece in request.stream():
                target.write(piece)
        else:
            raise HTTPException(
                status_code=415,
                detail="Send multipart/form-data with a 'file' field, "
                "or a raw body with Content-Type: application/x-ndjson",
            )

    with closing(connection(DB_PATH)) as conn, transaction(conn):
        save_job_file(conn, job_id, target.name)

    background_task.add_task(run_file, target.name, job_id)
    return {"job_id": job_id}


@app.post(
    "/v1/jobs/{job_id}/resume",
    status_code=202,
    summary="Resume an interrupted job",
    description=(
        "Restarts a job that crashed or was stopped, from its saved cursor. Events "
        "that were already committed are skipped, and saving is an upsert by "
        "`shipment_id`, so nothing is stored twice. Returns 202 with the number of "
        "events that will be skipped (`resume_from`). Returns 404 if the job is unknown."
    ),
    responses={404: {"description": "Unknown job_id"}},
)
def resume_job(job_id: str, background_task: BackgroundTasks) -> ResumeResponse:
    with closing(connection(DB_PATH)) as conn:
        path = get_job_file(conn, job_id)
        cursor = get_cursor(conn, job_id)

    if path is None:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found")

    background_task.add_task(run_file, path, job_id)
    return ResumeResponse(job_id=job_id, resume_from=cursor)


@app.get(
    "/v1/jobs/{job_id}/dlq",
    summary="List a job's quarantined records",
    description=(
        "Returns the records that failed parsing or validation for this job, with the "
        "original line and the error message, one page at a time. Use `limit` and "
        "`offset` to page through them; `total` is the number of records in the DLQ."
    ),
)
def get_job_dlq(
    job_id: str,
    limit: Annotated[int, Query(ge=1, le=1000, description="Records per page")] = 100,
    offset: Annotated[int, Query(ge=0, description="Records to skip")] = 0,
) -> DeadLetterPage:
    with closing(connection(DB_PATH)) as conn:
        total = count_dead_letters(conn, job_id)
        rows = list_dead_letters(conn, job_id, limit, offset)

    return DeadLetterPage(
        job_id=job_id,
        total=total,
        limit=limit,
        offset=offset,
        items=[DeadLetterItem(raw=raw, error=error) for raw, error in rows],
    )


@app.get(
    "/v1/jobs/{job_id}",
    summary="Get a job's result",
    description=(
        "Returns the record counts for a finished job: valid events per schema "
        "version (`v1`, `v2`) and the number of records sent to the DLQ (`dlq`). "
        "Returns 404 if the job does not exist or has not finished yet."
    ),
)
def get_job(job_id: str) -> dict[str, int]:
    job = jobs.get(job_id)

    if job is None:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found")
    return job
