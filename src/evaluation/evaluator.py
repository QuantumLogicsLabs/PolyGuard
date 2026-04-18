"""
evaluator.py
============
Evaluate the trained classifier on the test split.
Prints per-label precision, recall, F1, and overall metrics.
"""
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    classification_report,
    hamming_loss,
    jaccard_score,
)

from src.data_pipeline.code_dataset import CodeVulnerabilityDataset, LABEL_NAMES
from src.models.codebert_classifier import CodeBERTClassifier
from src.utils import get_logger, load_model_config, load_paths_config

logger = get_logger(__name__, log_file="experiments/logs/eval.log")


def evaluate(model_path: str = None, threshold: float = 0.5):
    model_cfg = load_model_config()
    paths_cfg = load_paths_config()

    model_path = model_path or paths_cfg["models"]["best_model"]
    test_path  = paths_cfg["data"]["test_file"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not Path(model_path).exists():
        logger.error(f"Model not found at {model_path}. Run training first.")
        return

    model = CodeBERTClassifier.load(
        model_path,
        model_name=model_cfg["model"]["base_model"],
        num_labels=model_cfg["model"]["num_labels"],
    ).to(device)

    test_ds = CodeVulnerabilityDataset(test_path, max_length=model_cfg["model"]["max_seq_length"])
    loader  = DataLoader(test_ds, batch_size=model_cfg["inference"]["batch_size"])

    all_probs  = []
    all_labels = []

    model.eval()
    with torch.no_grad():
        for batch in loader:
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].cpu().numpy()
            out = model(input_ids=input_ids, attention_mask=attention_mask)
            probs = out["probs"].cpu().numpy()
            all_probs.append(probs)
            all_labels.append(labels)

    y_prob = np.concatenate(all_probs)
    y_true = np.concatenate(all_labels)
    y_pred = (y_prob >= threshold).astype(int)

    report = classification_report(y_true, y_pred, target_names=LABEL_NAMES, zero_division=0)
    logger.info(f"\n{report}")
    print(report)

    hl = hamming_loss(y_true, y_pred)
    js = jaccard_score(y_true, y_pred, average="samples", zero_division=0)
    logger.info(f"Hamming Loss : {hl:.4f}")
    logger.info(f"Jaccard Score: {js:.4f}")
    print(f"Hamming Loss : {hl:.4f}")
    print(f"Jaccard Score: {js:.4f}")

    return {"report": report, "hamming_loss": hl, "jaccard_score": js}


if __name__ == "__main__":
    evaluate()
