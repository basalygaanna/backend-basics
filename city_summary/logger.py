import logging
import sys
import uuid


def setup_logging() -> str:
    run_id = str(uuid.uuid4())
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s %(levelname)s run_id={run_id} %(name)s: %(message)s",
        stream=sys.stderr,
    )
    return run_id
