from __future__ import annotations

import numpy as np
import gymnasium as gym
import gymnasium.spaces as spaces
from pathlib import Path
from stable_baselines3 import PPO
from stable_baselines3.common.policies import ActorCriticCnnPolicy

from training.actions import N_ACTIONS
from training.vision import FRAME_STACK, FRAME_W, FRAME_H

OBS_SHAPE = (FRAME_STACK, FRAME_H, FRAME_W)


class _DummyEnv(gym.Env):
    """Minimal env to satisfy SB3's constructor signature when loading a checkpoint."""
    observation_space = spaces.Box(0.0, 1.0, shape=OBS_SHAPE, dtype=np.float32)
    action_space = spaces.Discrete(N_ACTIONS)

    def reset(self, **kw):
        return np.zeros(OBS_SHAPE, np.float32), {}

    def step(self, action):
        return np.zeros(OBS_SHAPE, np.float32), 0.0, False, False, {}


class BR2Agent:
    def __init__(self, model_path: str | None = None, device: str = "auto") -> None:
        self.device = device
        if model_path and Path(model_path).exists():
            self.model = PPO.load(model_path, env=_DummyEnv(), device=device)
        else:
            self.model = PPO(
                ActorCriticCnnPolicy,
                _DummyEnv(),
                verbose=1,
                device=device,
                tensorboard_log="logs/",
                n_steps=512,
                batch_size=64,
                n_epochs=4,
                gamma=0.99,
                learning_rate=2.5e-4,
                clip_range=0.1,
            )

    def act(self, obs: np.ndarray, deterministic: bool = True) -> int:
        """Predict a discrete action index from a (n_stack, H, W) observation."""
        action, _ = self.model.predict(obs[np.newaxis, ...], deterministic=deterministic)
        return int(action[0])

    def save(self, path: str) -> None:
        self.model.save(path)
