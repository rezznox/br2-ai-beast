"""DuckStation window capture using dxcam (Windows only).

Finds the DuckStation window by title, captures its region at target_fps using
the DXGI Desktop Duplication API, and yields JPEG-compressed bytes per frame.
Much faster than mss — capable of 240+ FPS; we cap at 60 to match emulator output.
"""

from __future__ import annotations

import io
import os
from typing import Generator

import dxcam
import pygetwindow as gw
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

WINDOW_TITLE = os.getenv("DUCKSTATION_WINDOW_TITLE", "DuckStation")
TARGET_FPS = 20
JPEG_QUALITY = 85


def _get_window_region() -> tuple[int, int, int, int]:
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        raise RuntimeError(
            f"No window titled '{WINDOW_TITLE}' found. "
            "Make sure DuckStation is open and the title matches."
        )
    win = windows[0]
    print((win.left, win.top, win.right, win.bottom))
    # dxcam region is (left, top, right, bottom)
    return (win.left, win.top, win.right, win.bottom)


def frame_generator() -> Generator[bytes, None, None]:
    """Yield JPEG-encoded frame bytes from the DuckStation window at TARGET_FPS."""
    region = _get_window_region()
    camera = dxcam.create(region=region, output_color="BGR")
    camera.start(target_fps=TARGET_FPS)

    try:
        while True:
            frame = camera.get_latest_frame()
            if frame is None:
                continue

            # Convert BGR numpy array → JPEG bytes
            img = Image.fromarray(frame[:, :, ::-1])  # BGR → RGB for Pillow
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=JPEG_QUALITY)
            yield buf.getvalue()
    finally:
        camera.stop()
        camera.release()
