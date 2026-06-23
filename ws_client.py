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

from capture import frame_generator
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
    return p.parse_args()


async def run(host: str, port: int) -> None:
    uri = f"ws://{host}:{port}/ws"
    controller = VirtualController()
    logger.info("Connecting to %s …", uri)

    async with websockets.connect(uri, max_size=10 * 1024 * 1024) as ws:
        logger.info("Connected. Starting frame loop.")
        frames = frame_generator()
        os.makedirs('frames', exist_ok=True)
        i = 0
        try:
            for frame_bytes in frames:
                await ws.send(frame_bytes)
                image = Image.open(io.BytesIO(frame_bytes))
                image.save('frames/test-{}.jpg'.format(i))
                i = i + 1
                if i > 20:
                    break
                """ raw = await ws.recv()
                data = json.loads(raw)
                controller.press(data["buttons"])
                logger.debug("action=%s buttons=%s", data["action_name"], data["buttons"]) """
        except websockets.ConnectionClosed as exc:
            logger.warning("Server closed connection: %s", exc)
        finally:
            controller.release_all()


def main() -> None:
    args = parse_args()
    try:
        asyncio.run(run(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
