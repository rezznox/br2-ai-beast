from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from capture.capture import _get_window_region, frame_generator, TARGET_FPS


def _fake_bgr_frame(w: int = 320, h: int = 240) -> np.ndarray:
    return np.zeros((h, w, 3), dtype=np.uint8)


def _make_mock_window(left=10, top=20, right=800, bottom=600):
    win = MagicMock()
    win.left = left
    win.top = top
    win.right = right
    win.bottom = bottom
    return win


@patch("pygetwindow.getWindowsWithTitle")
def test_window_region_returns_coordinates(mock_gw):
    mock_gw.return_value = [_make_mock_window(10, 20, 800, 600)]
    assert _get_window_region() == (10, 20, 800, 600)


# ---------------------------------------------------------------------------
# frame_generator
# ---------------------------------------------------------------------------

@patch("dxcam.create")
@patch("pygetwindow.getWindowsWithTitle")
def test_frame_generator_yields_jpeg(mock_gw, mock_create):
    mock_gw.return_value = [_make_mock_window()]
    camera = MagicMock()
    camera.get_latest_frame.return_value = _fake_bgr_frame()
    mock_create.return_value = camera

    gen = frame_generator()
    frames = [next(gen) for _ in range(3)]
    gen.close()

    for frame_bytes in frames:
        assert frame_bytes[:2] == b"\xff\xd8", "Expected JPEG magic bytes"


@patch("dxcam.create")
@patch("pygetwindow.getWindowsWithTitle")
def test_camera_started_with_target_fps(mock_gw, mock_create):
    mock_gw.return_value = [_make_mock_window()]
    camera = MagicMock()
    camera.get_latest_frame.return_value = _fake_bgr_frame()
    mock_create.return_value = camera

    gen = frame_generator()
    next(gen)
    gen.close()

    camera.start.assert_called_once_with(target_fps=TARGET_FPS)


@patch("dxcam.create")
@patch("pygetwindow.getWindowsWithTitle")
def test_none_frames_are_skipped(mock_gw, mock_create):
    mock_gw.return_value = [_make_mock_window()]
    camera = MagicMock()
    # None, None, then a real frame; list exhausted → StopIteration propagates out
    camera.get_latest_frame.side_effect = [None, None, _fake_bgr_frame()]
    mock_create.return_value = camera

    gen = frame_generator()
    try:
        frame = next(gen)
    except StopIteration:
        pytest.fail("Generator yielded nothing but should have skipped Nones and yielded 1 frame")

    gen.close()

    assert frame[:2] == b"\xff\xd8"
    assert camera.get_latest_frame.call_count == 3


@patch("dxcam.create")
@patch("pygetwindow.getWindowsWithTitle")
def test_camera_cleanup_on_generator_close(mock_gw, mock_create):
    mock_gw.return_value = [_make_mock_window()]
    camera = MagicMock()
    camera.get_latest_frame.return_value = _fake_bgr_frame()
    mock_create.return_value = camera

    gen = frame_generator()
    next(gen)
    gen.close()

    camera.stop.assert_called_once()
    camera.release.assert_called_once()


@patch("dxcam.create")
@patch("pygetwindow.getWindowsWithTitle")
def test_fps_rate(mock_gw, mock_create):
    mock_gw.return_value = [_make_mock_window()]
    camera = MagicMock()
    delay = 1.0 / TARGET_FPS

    def _frame_with_sleep():
        time.sleep(delay)
        return _fake_bgr_frame()

    camera.get_latest_frame.side_effect = _frame_with_sleep
    mock_create.return_value = camera

    n = 5
    gen = frame_generator()
    t0 = time.perf_counter()
    for _ in range(n):
        next(gen)
    elapsed = time.perf_counter() - t0
    gen.close()

    expected = n * delay
    assert expected * 0.5 <= elapsed <= expected * 2.0, (
        f"Expected ~{expected:.2f}s for {n} frames at {TARGET_FPS} FPS, got {elapsed:.2f}s"
    )
