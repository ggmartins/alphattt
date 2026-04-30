#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "fastapi==0.136.1",
#   "uvicorn[standard]==0.46.0",
# ]
# ///

from fastapi import FastAPI
import os
import uvicorn
import argparse

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "Hello from FastAPI running in Kubernetes with uv!",
        "db_host": os.getenv("DB_HOST", "not set"),
        "db_name": os.getenv("DB_NAME", "not set"),
    }

@app.get("/health")
def health():
    return {"status": "ok"}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the FastAPI app."
    )

    parser.add_argument(
        "--check",
        default="db",
        help="Check DB",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
    )


