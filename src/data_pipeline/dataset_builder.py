"""
dataset_builder.py
==================
Builds train/val/test splits from raw vulnerability samples.
Saves processed JSON files to data/processed/.
"""
import json
import random
from pathlib import Path
from typing import List, Dict, Any

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


def load_raw_samples(raw_dir: str) -> List[Dict[str, Any]]:
    """Load all JSON sample files from the raw data directory."""
    raw_path = Path(raw_dir)
    samples = []
    for json_file in raw_path.glob("**/*.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                samples.extend(data)
            elif isinstance(data, dict):
                samples.append(data)
    logger.info(f"Loaded {len(samples)} raw samples from {raw_dir}")
    return samples


def validate_sample(sample: Dict[str, Any]) -> bool:
    """Check that a sample has required fields."""
    required = ["code", "language", "labels"]
    return all(k in sample for k in required)


def build_splits(
    samples: List[Dict[str, Any]],
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    seed: int = 42,
) -> Dict[str, List[Dict[str, Any]]]:
    """Shuffle and split samples into train/val/test."""
    random.seed(seed)
    valid = [s for s in samples if validate_sample(s)]
    logger.info(f"{len(valid)} valid samples after filtering")
    random.shuffle(valid)

    n = len(valid)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    return {
        "train": valid[:n_train],
        "val": valid[n_train : n_train + n_val],
        "test": valid[n_train + n_val :],
    }


def save_splits(splits: Dict[str, List], processed_dir: str) -> None:
    """Save each split to a JSON file."""
    out_path = Path(processed_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    for split_name, data in splits.items():
        out_file = out_path / f"{split_name}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(data)} samples → {out_file}")


def build_dataset(raw_dir: str = "data/raw", processed_dir: str = "data/processed") -> None:
    """End-to-end dataset build: raw → splits."""
    samples = load_raw_samples(raw_dir)
    if not samples:
        logger.warning("No raw samples found. Generate synthetic data first.")
        _generate_synthetic_samples(raw_dir)
        samples = load_raw_samples(raw_dir)

    splits = build_splits(samples)
    save_splits(splits, processed_dir)
    logger.info("Dataset build complete.")


# ---------------------------------------------------------------------------
# Synthetic sample generation (for demo / smoke testing without real data)
# ---------------------------------------------------------------------------

SYNTHETIC_SAMPLES = [
    {
        "code": 'query = "SELECT * FROM users WHERE id = " + user_id\ncursor.execute(query)',
        "language": "python",
        "labels": ["sql_injection"],
        "source": "synthetic",
    },
    {
        "code": "document.innerHTML = userInput;",
        "language": "javascript",
        "labels": ["xss"],
        "source": "synthetic",
    },
    {
        "code": 'char buf[64];\nstrcpy(buf, argv[1]);  // no bounds check',
        "language": "cpp",
        "labels": ["buffer_overflow"],
        "source": "synthetic",
    },
    {
        "code": 'API_KEY = "sk-abc123supersecret"\npassword = "hunter2"',
        "language": "python",
        "labels": ["hardcoded_secret"],
        "source": "synthetic",
    },
    {
        "code": "import hashlib\nhash = hashlib.md5(data).hexdigest()",
        "language": "python",
        "labels": ["weak_crypto"],
        "source": "synthetic",
    },
    {
        "code": "def login(user, pwd):\n    if pwd == stored_password:  # plaintext compare\n        return True",
        "language": "python",
        "labels": ["broken_auth"],
        "source": "synthetic",
    },
    {
        "code": "cursor.execute('SELECT * FROM products WHERE name = %s', (name,))",
        "language": "python",
        "labels": [],
        "source": "synthetic",
    },
    {
        "code": "const safe = document.createTextNode(userInput);\ndiv.appendChild(safe);",
        "language": "javascript",
        "labels": [],
        "source": "synthetic",
    },
]


def _generate_synthetic_samples(raw_dir: str) -> None:
    """Write synthetic samples to data/raw/synthetic.json."""
    raw_path = Path(raw_dir)
    raw_path.mkdir(parents=True, exist_ok=True)
    out = raw_path / "synthetic.json"
    with open(out, "w") as f:
        json.dump(SYNTHETIC_SAMPLES * 20, f, indent=2)  # repeat for larger set
    logger.info(f"Generated {len(SYNTHETIC_SAMPLES) * 20} synthetic samples → {out}")


if __name__ == "__main__":
    build_dataset()
