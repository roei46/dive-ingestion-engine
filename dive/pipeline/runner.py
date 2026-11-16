from dive.pipeline.dlq import DeadLetterQueue
from dive.pipeline.pipeline import parse_json, read_lines, validate

jobs: dict[str, dict[str, int]] = {}

def run_file(path: str, job_id: str) -> dict[str, int]:
    dlq = DeadLetterQueue()
    counts: dict[str, int] = {}

    lines = read_lines(path=path)
    raw = parse_json(dlq=dlq, lines=lines)
    events = validate(dlq=dlq, dicts=raw)

    for event in events:
        counts[event.version] = counts.get(event.version, 0) + 1

    counts["dlq"] = len(dlq.dead_letters)
    jobs[job_id] = counts

    print("counts is: ", counts)
    return counts
