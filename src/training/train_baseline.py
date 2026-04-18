"""
train_baseline.py
=================
Train the TF-IDF + LightGBM baseline (Experiment 01).

Usage:
    python -m src.training.train_baseline
"""
import json
from src.models.baseline_model import BaselineModel
from src.utils import get_logger, load_paths_config

logger = get_logger(__name__, log_file="experiments/logs/baseline.log")


def train_baseline():
    paths = load_paths_config()
    train_path  = paths["data"]["train_file"]
    model_path  = paths["models"]["baseline_model"]

    with open(train_path, "r") as f:
        train_samples = json.load(f)

    model = BaselineModel()
    model.fit(train_samples)
    model.save(model_path)
    logger.info(f"Baseline saved → {model_path}")


if __name__ == "__main__":
    train_baseline()
