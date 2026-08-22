#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "cryptography",
#   "fastapi==0.136.1",
#   "pymysql==1.1.2",
#   "sqlalchemy==2.0.49",
#   "sqlmodel==0.0.38",
#   "uvicorn[standard]==0.46.0",
# ]
# ///

import sys
import logging
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

__version__ = "1.0.0a4"

from db.db import DB
from controller import Controller

import os
import json
import uvicorn
import argparse

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format=(
        "%(asctime)s %(levelname)s %(name)s "
        "event=%(event)s %(message)s"
    ),
)
logger = logging.getLogger(__name__)


app = FastAPI()

#MySQL sqlmodel sql alchemy Connect String with os.getenv("DB_HOST")
db_connection_string = \
    f"mysql+pymysql://" + \
    f"{os.getenv('DB_USER')}:" + \
    f"{os.getenv('DB_PASSWORD')}" + \
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

logger.info(f"DB Connection String: " + \
            f"mysql+pymysql://...%s/%s ", os.getenv("DB_HOST"), os.getenv("DB_NAME"),
            extra={"event": "db_connection_string"})

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
def read_root() -> HTMLResponse:
    return HTMLResponse(f""" 
            <!DOCTYPE html>
            <html>
            <head>
                <title>Alpha TTT Board API v.{__version__}</title>
            </head>
            <body>
                <H1>
                <a href="/docs">Alpha TTT Board API v.{__version__}</a>
                </H1>
            </body>
            </html>
        """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    client = websocket.client
    source_ip : str = client.host if client else "unknown"
    source_port : int = client.port if client else None
    await websocket.accept()
    controller : Controller = Controller(db)
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Echoing: %s", data, extra={"event": "websocket_echo"})
            if not controller:
                logger.warning("Controller is not initialized",
                    extra={"event": "websocket_controller_not_initialized"}
                )
                continue

            result, close = await controller.handle_websocket_message(data, source_ip, source_port)

            if close:
                await websocket_close(websocket)
                break

            await websocket.send_text(f"{json.dumps({'echo': data})}")
            await websocket.send_text(f"{json.dumps(result)}")

    except WebSocketDisconnect as wsd:
        logger.info(f"Client disconnected: %s (%s:%s)",
            str(wsd), source_ip, source_port,
            extra={"event": "websocket_disconnect"}
        )

async def websocket_close(websocket: WebSocket) -> None:
    await websocket.close()
    logger.info(f"WebSocket close commanded %s:%s", websocket.client.host, websocket.client.port,
        extra={"event": "websocket_close"}
    )

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Alpha TTT app."
    )

    parser.add_argument(
        "--check",
        default="db",
        help="Check DB",
    )

    parser.add_argument(
        "--port",
        default="8000",
        help="TCP Port to use.",
    )


    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=int(args.port),
    )


