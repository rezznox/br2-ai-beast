from __future__ import annotations

import argparse
import logging
import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="BR2-AI-Beast: RL agent for Bloody Roar 2")
    p.add_argument("--mode", choices=["inference", "train"], default="inference")
    p.add_argument(
        "--model",
        default=os.getenv("MODEL_PATH", "models/ppo_br2.zip"),
        help="Path to a saved SB3 model checkpoint (.zip)",
    )
    p.add_argument("--host", default=os.getenv("WS_HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.getenv("WS_PORT", "8765")))
    p.add_argument(
        "--timesteps",
        type=int,
        default=1_000_000,
        help="Total environment timesteps for training mode",
    )
    return p.parse_args()


def run_inference(args: argparse.Namespace) -> None:
    from training.server import app, init_server
    """ init_server(model_path=args.model) """
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


def run_training(args: argparse.Namespace) -> None:
    from training.train import run_training_loop
    run_training_loop(
        model_path=args.model,
        total_timesteps=args.timesteps,
    )


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "inference":
        run_inference(args)
    else:
        run_training(args)
