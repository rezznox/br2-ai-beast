from __future__ import annotations

import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from training.vision import FrameStacker, decode_frame, preprocess_frame
from training.agent import BR2Agent

logger = logging.getLogger(__name__)

app = FastAPI(title="BR2-AI-Beast")

_agent: BR2Agent | None = None
_stacker: FrameStacker | None = None


def init_server(model_path: str | None = None) -> None:
    """Inject the agent and frame stacker before uvicorn starts serving."""
    global _agent, _stacker
    _agent = BR2Agent(model_path=model_path)
    _stacker = FrameStacker()
    logger.info("Agent initialized (model_path=%s)", model_path)


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok", "agent_loaded": _agent is not None})


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    logger.info("Capture client connected: %s", websocket.client)
    """ _stacker.reset() """

    try:
        while True:
            raw_bytes = await websocket.receive_bytes()

            frame = decode_frame(raw_bytes)
            processed = preprocess_frame(frame)
            """ obs = _stacker.push(processed)

            action_idx = _agent.act(obs, deterministic=True)
            buttons = action_to_buttons(action_idx)

            await websocket.send_json({
                "action": action_idx,
                "buttons": [b.value for b in buttons],
                "action_name": action_name(action_idx),
            }) """
    except WebSocketDisconnect:
        logger.info("Capture client disconnected.")
    except Exception as exc:
        logger.exception("WebSocket error: %s", exc)
        await websocket.close(code=1011)
