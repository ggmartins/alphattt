#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "fastapi==0.136.1",
#   "pymysql==1.1.2",
#   "sqlalchemy==2.0.49",
#   "sqlmodel==0.0.38",
#   "uvicorn[standard]==0.46.0",
# ]
# ///

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from db.db import DB

import os
import uvicorn
import argparse

app = FastAPI()

#MySQL sqlmodel sql alchemy Connect String with os.getenv("DB_HOST")
db_connection_string = \
    f"mysql+pymysql://" + \
    f"{os.getenv('DB_USER')}:" + \
    f"{os.getenv('DB_PASSWORD')}" + \
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

db = DB(db_connection_string)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return HTMLResponse(f"""
    <h1>FastAPI WebSocket Template backend is running (v2).</h1>
    <p>db_connection_string: {db_connection_string}</p>
    <p>Angular should connect to <code>ws://localhost:8000/ws</code></p>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Echoing: {data}")

            await websocket.send_text(f"Echo: {data}")

    except WebSocketDisconnect:
        print("Client disconnected")

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


