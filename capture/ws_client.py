"""Windows-side WebSocket client.

Captures DuckStation frames with dxcam, sends each frame to the WSL2 inference
server, receives the action JSON, and presses the corresponding buttons on the
virtual Xbox360 controller (vgamepad / ViGEm).

Usage (from PowerShell):
    python ws_client.py --host <WSL2-IP> --port 8765

Find your WSL2 IP:
    wsl hostname -I
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import io
import sys
from PIL import Image

import websockets
from dotenv import load_dotenv

load_dotenv()

from capture.capture import frame_generator
from controller import VirtualController

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="BR2-AI-Beast capture client")
    p.add_argument("--host", default=os.getenv("WS_HOST", "127.0.0.1"))
    p.add_argument("--port", type=int, default=int(os.getenv("WS_PORT", "8765")))
    p.add_argument("--control", type=bool, default=bool(os.getenv("CONTROL", False)))
    p.add_argument("--capture_frames", type=bool, default=bool(os.getenv("CAPTURE_FRAMES", False)))
    return p.parse_args()

async def send_frames(ws: websockets.WebSocketClientProtocol, capture: bool):
        logger.info("Connected. Starting frame loop.")
        frames = frame_generator()
        _capture = capture and os.makedirs('frames', exist_ok=True)
        i = 0
        try:
            for frame_bytes in frames:
                if _capture:
                    image = Image.open(io.BytesIO(frame_bytes))
                    image.save('frames/test-{}.jpg'.format(i))
                    i = i + 1
                    if i > 20:
                        break
                else:
                    await ws.send(frame_bytes)
        except websockets.ConnectionClosed as exc:
            logger.warning("Server closed connection: %s", exc)
        finally:
            logger.info("Finally reached in send frames")
            """ controller.release_all() """

async def rcv_commands(ws: websockets.WebSocketClientProtocol, control: bool):
        logger.info("Connected. Starting command loop.")
        vc = VirtualController(control)
        try:
            while True:
                raw = await ws.recv()
                data = json.loads(raw)
                vc.press(data["buttons"])
                logger.debug("action=%s buttons=%s", data["action_name"], data["buttons"])
        except websockets.ConnectionClosed as exc:
            logger.warning("Server closed connection: %s", exc)
        finally:
            logger.info("Finally reached in rcv commands")
            vc.release_all()

async def run(host: str, port: int, control: bool, capture_frames: bool) -> None:
    uri = f"ws://{host}:{port}/ws"
    logger.info("Connecting to %s …", uri)
    async with websockets.connect(uri, max_size=10 * 1024 * 1024) as ws:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(send_frames(ws, capture_frames))
            tg.create_task(rcv_commands(ws, control))

def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.host, args.port, args.control, args.capture_frames))
    except KeyboardInterrupt:
        logger.info("Stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()
