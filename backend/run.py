import os
import sys

is_dev = "--dev" in sys.argv
if is_dev:
    os.environ["DATABASE_URL"] = "sqlite:///./dev.db"
    sys.argv.remove("--dev")

import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=is_dev)
