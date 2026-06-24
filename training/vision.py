import cv2
import numpy as np
from collections import deque

FRAME_W = 84
FRAME_H = 84
FRAME_STACK = 4


def decode_frame(raw_bytes: bytes) -> np.ndarray:
    """Decode JPEG/PNG bytes from the Windows capture client into an HxWx3 BGR array."""
    arr = np.frombuffer(raw_bytes, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode frame — not a valid JPEG/PNG payload")
    return frame


def preprocess_frame(
    frame: np.ndarray,
    width: int = FRAME_W,
    height: int = FRAME_H,
) -> np.ndarray:
    """Resize to (H, W), convert to grayscale, normalize to float32 [0, 1]."""
    resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    return gray.astype(np.float32) / 255.0


class FrameStacker:
    """Rolling buffer of the last N preprocessed frames.

    Returns a (n_stack, H, W) observation array on each push(), which is the
    standard input format for SB3's CnnPolicy.
    """

    def __init__(
        self,
        n_stack: int = FRAME_STACK,
        width: int = FRAME_W,
        height: int = FRAME_H,
    ) -> None:
        self.n_stack = n_stack
        self.width = width
        self.height = height
        self._frames: deque[np.ndarray] = deque(
            [np.zeros((height, width), dtype=np.float32)] * n_stack,
            maxlen=n_stack,
        )

    def push(self, frame: np.ndarray) -> np.ndarray:
        """Append a preprocessed frame and return the full stacked observation."""
        self._frames.append(frame)
        return np.stack(list(self._frames), axis=0)

    def reset(self) -> np.ndarray:
        blank = np.zeros((self.height, self.width), dtype=np.float32)
        self._frames = deque([blank] * self.n_stack, maxlen=self.n_stack)
        return np.stack(list(self._frames), axis=0)
