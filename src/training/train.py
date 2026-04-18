"""
train.py
========
Training loop for the CodeBERT multi-label classifier.

Usage:
    python -m src.training.train
"""
import json
import os
from pathlib import Path

import torch
from torch.utils.data import DataLoader
from transformers import get_linear_schedule_with_warmup

from src.data_pipeline.code_dataset import CodeVulnerabilityDataset
from src.models.codebert_classifier import CodeBERTClassifier
from src.utils import get_logger, load_model_config, load_paths_config

logger = get_logger(__name__, log_file="experiments/logs/train.log")


def train(config_override: dict = None):
    model_cfg = load_model_config()
    paths_cfg = load_paths_config()
    cfg = model_cfg if not config_override else {**model_cfg, **config_override}

    # ── Paths ─────────────────────────────────────────────────────────────────
    train_path = paths_cfg["data"]["train_file"]
    val_path   = paths_cfg["data"]["val_file"]
    save_dir   = paths_cfg["models"]["save_dir"]
    best_path  = paths_cfg["models"]["best_model"]
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    # ── Device ────────────────────────────────────────────────────────────────
    device_name = cfg["inference"]["device"]
    device = torch.device("cuda" if torch.cuda.is_available() and device_name == "cuda" else "cpu")
    logger.info(f"Training on device: {device}")

    # ── Data ──────────────────────────────────────────────────────────────────
    train_ds = CodeVulnerabilityDataset(train_path, max_length=cfg["model"]["max_seq_length"])
    val_ds   = CodeVulnerabilityDataset(val_path,   max_length=cfg["model"]["max_seq_length"])

    train_loader = DataLoader(train_ds, batch_size=cfg["training"]["batch_size"], shuffle=True)
    val_loader   = DataLoader(val_ds,   batch_size=cfg["training"]["batch_size"])

    # ── Model ─────────────────────────────────────────────────────────────────
    model = CodeBERTClassifier(
        model_name=cfg["model"]["base_model"],
        num_labels=cfg["model"]["num_labels"],
        dropout=cfg["model"]["hidden_dropout_prob"],
    ).to(device)

    # ── Optimizer / Scheduler ─────────────────────────────────────────────────
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg["training"]["learning_rate"],
        weight_decay=cfg["training"]["weight_decay"],
    )
    total_steps = len(train_loader) * cfg["training"]["epochs"]
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=cfg["training"]["warmup_steps"],
        num_training_steps=total_steps,
    )

    best_val_loss = float("inf")
    patience_counter = 0

    for epoch in range(1, cfg["training"]["epochs"] + 1):
        # ── Train ──────────────────────────────────────────────────────────
        model.train()
        total_loss = 0.0
        for step, batch in enumerate(train_loader):
            input_ids      = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels         = batch["labels"].to(device)

            optimizer.zero_grad()
            out = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = out["loss"]
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["training"]["gradient_clip"])
            optimizer.step()
            scheduler.step()
            total_loss += loss.item()

            if (step + 1) % 50 == 0:
                logger.info(f"  Epoch {epoch} | Step {step+1}/{len(train_loader)} | Loss: {loss.item():.4f}")

        avg_train_loss = total_loss / len(train_loader)

        # ── Validation ─────────────────────────────────────────────────────
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in val_loader:
                input_ids      = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels         = batch["labels"].to(device)
                out = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                val_loss += out["loss"].item()
        avg_val_loss = val_loss / max(len(val_loader), 1)

        logger.info(
            f"Epoch {epoch}/{cfg['training']['epochs']} | "
            f"Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}"
        )

        # ── Checkpointing ──────────────────────────────────────────────────
        ckpt_path = f"{save_dir}/checkpoint_epoch_{epoch}.pt"
        model.save(ckpt_path)

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            patience_counter = 0
            model.save(best_path)
            logger.info(f"  ✅ New best model saved → {best_path}")
        else:
            patience_counter += 1
            if patience_counter >= cfg["training"]["early_stopping_patience"]:
                logger.info("Early stopping triggered.")
                break

    logger.info("Training complete.")


if __name__ == "__main__":
    train()
