import io
import json
import numpy as np
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from training.server import app, init_server


@pytest.fixture(autouse=True)
def setup_server():
    init_server(model_path=None)


def _make_jpeg() -> bytes:
    img = Image.fromarray(np.zeros((240, 320, 3), dtype=np.uint8))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_health():
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["agent_loaded"] is True


def test_websocket_returns_action():
    client = TestClient(app)
    with client.websocket_connect("/ws") as ws:
        ws.send_bytes(_make_jpeg())
        raw = ws.receive_text()
        data = json.loads(raw)
        assert "action" in data
        assert "buttons" in data
        assert "action_name" in data
        assert isinstance(data["action"], int)
        assert 0 <= data["action"] <= 17
