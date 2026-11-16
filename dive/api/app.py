import tempfile
import uuid

from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile

from dive.pipeline.runner import jobs, run_file

app = FastAPI()


@app.post("/v1/ingest", status_code=202)
async def ingest_file(
    file: UploadFile, background_task: BackgroundTasks
) -> dict[str, str]:
    job_id = str(uuid.uuid4())
    result = {"job_id": job_id}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".ndjson") as target:
        while True:
            piece = await file.read(1024 * 1024)
            if not piece:
                break
            target.write(piece)

    background_task.add_task(run_file, target.name, job_id)
    return result


@app.get("/v1/jobs/{job_id}")
def get_job(job_id: str) -> dict[str, int]:
    job = jobs.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=404, detail=f"Job with ID '{job_id}' not found"
        )
    return job


