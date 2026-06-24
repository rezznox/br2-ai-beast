from __future__ import annotations

import logging

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback

from training.env import BloodyRoar2Env

logger = logging.getLogger(__name__)


def run_training_loop(
    model_path: str,
    total_timesteps: int,
) -> None:
    env = DummyVecEnv([BloodyRoar2Env])

    checkpoint_cb = CheckpointCallback(
        save_freq=10_000,
        save_path="models/",
        name_prefix="ppo_br2",
        verbose=1,
    )

    model = PPO(
        "CnnPolicy",
        env,
        verbose=1,
        device="auto",
        tensorboard_log="logs/",
        n_steps=512,
        batch_size=64,
        n_epochs=4,
        gamma=0.99,
        learning_rate=2.5e-4,
        clip_range=0.1,
    )

    logger.info("Starting PPO training for %d timesteps", total_timesteps)
    model.learn(
        total_timesteps=total_timesteps,
        callback=checkpoint_cb,
        progress_bar=True,
    )
    model.save(model_path)
    logger.info("Model saved to %s", model_path)
