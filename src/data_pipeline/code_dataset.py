"""
code_dataset.py
===============
PyTorch Dataset that loads processed JSON splits.
"""
import json
from pathlib import Path
from typing import List, Dict, Any

import torch
from torch.utils.data import Dataset

from src.data_pipeline.tokenizer import tokenize_code
from src.utils import get_logger

logger = get_logger(__name__)

LABEL_NAMES = [
    "sql_injection",
    "xss",
    "buffer_overflow",
    "hardcoded_secret",
    "weak_crypto",
    "broken_auth",
]


class CodeVulnerabilityDataset(Dataset):
    """
    Loads code samples and converts labels to multi-hot vectors.
    """

    def __init__(self, json_path: str, max_length: int = 512):
        self.max_length = max_length
        with open(json_path, "r", encoding="utf-8") as f:
            self.samples: List[Dict[str, Any]] = json.load(f)
        logger.info(f"Loaded {len(self.samples)} samples from {json_path}")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        sample = self.samples[idx]
        code = sample.get("code", "")
        label_list: List[str] = sample.get("labels", [])

        encoding = tokenize_code(code, max_length=self.max_length)

        # Multi-hot label vector
        labels = torch.zeros(len(LABEL_NAMES), dtype=torch.float)
        for lbl in label_list:
            if lbl in LABEL_NAMES:
                labels[LABEL_NAMES.index(lbl)] = 1.0

        return {
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "labels": labels,
        }
