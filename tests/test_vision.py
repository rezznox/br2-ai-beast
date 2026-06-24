import io
import numpy as np
from PIL import Image
from training.vision import decode_frame, preprocess_frame, FrameStacker, FRAME_W, FRAME_H, FRAME_STACK


def _make_jpeg(width=320, height=240) -> bytes:
    img = Image.fromarray(np.random.randint(0, 255, (height, width, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_decode_frame():
    frame = decode_frame(_make_jpeg())
    assert frame.ndim == 3
    assert frame.shape[2] == 3


def test_preprocess_shape():
    frame = decode_frame(_make_jpeg())
    out = preprocess_frame(frame)
    assert out.shape == (FRAME_H, FRAME_W)
    assert out.dtype == np.float32
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_frame_stacker():
    stacker = FrameStacker()
    obs = stacker.reset()
    assert obs.shape == (FRAME_STACK, FRAME_H, FRAME_W)

    frame = preprocess_frame(decode_frame(_make_jpeg()))
    obs = stacker.push(frame)
    assert obs.shape == (FRAME_STACK, FRAME_H, FRAME_W)
