"""Custom gymnasium environment that wraps the DuckStation emulator connection.

The emulator side (capture_client/ws_client.py on Windows) acts as the environment
source: it sends frames and receives actions. During training, this env is driven by
the SB3 training loop — each call to step() blocks until the next frame arrives over
the WebSocket connection established by the capture client.

The reward signal must be extracted from game memory or encoded into the frame stream
by the capture client. Until that integration is built, step() returns placeholder
values so the rest of the training pipeline can be tested end-to-end.
"""

from __future__ import annotations

import numpy as np
import gymnasium as gym
import gymnasium.spaces as spaces

from training.vision import FRAME_STACK, FRAME_H, FRAME_W, FrameStacker
from training.actions import N_ACTIONS

OBS_SHAPE = (FRAME_STACK, FRAME_H, FRAME_W)


class BloodyRoar2Env(gym.Env):
    metadata = {"render_modes": []}

    def __init__(self) -> None:
        super().__init__()
        self.observation_space = spaces.Box(0.0, 1.0, shape=OBS_SHAPE, dtype=np.float32)
        self.action_space = spaces.Discrete(N_ACTIONS)
        self._stacker = FrameStacker()

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        obs = self._stacker.reset()
        return obs, {}

    def step(self, action: int):
        # TODO: replace with real emulator frame + reward via WebSocket
        obs = self._stacker.push(np.zeros((FRAME_H, FRAME_W), dtype=np.float32))
        reward = 0.0
        terminated = False
        truncated = False
        info: dict = {}
        return obs, reward, terminated, truncated, info

    def render(self) -> None:
        pass

    def close(self) -> None:
        pass
