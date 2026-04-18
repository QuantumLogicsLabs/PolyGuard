"""
baseline_model.py
=================
TF-IDF + LightGBM multi-label baseline (Experiment 01).
Fast to train, interpretable, good sanity-check benchmark.
"""
import json
import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer

try:
    import lightgbm as lgb
    _HAS_LGB = True
except ImportError:
    from sklearn.linear_model import LogisticRegression
    _HAS_LGB = False

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


class BaselineModel:
    """TF-IDF + multi-label classifier baseline."""

    def __init__(self, max_features: int = 20_000, ngram_range: Tuple = (1, 3)):
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            ngram_range=ngram_range,
            analyzer="char_wb",
            sublinear_tf=True,
        )
        self.mlb = MultiLabelBinarizer(classes=LABEL_NAMES)
        base = (
            lgb.LGBMClassifier(n_estimators=200, learning_rate=0.1, num_leaves=31)
            if _HAS_LGB
            else LogisticRegression(max_iter=500, C=1.0)
        )
        self.clf = OneVsRestClassifier(base)

    def fit(self, samples: List[Dict]) -> None:
        codes = [s["code"] for s in samples]
        raw_labels = [s.get("labels", []) for s in samples]
        X = self.vectorizer.fit_transform(codes)
        y = self.mlb.fit_transform(raw_labels)
        logger.info(f"Training baseline on {len(codes)} samples…")
        self.clf.fit(X, y)
        logger.info("Baseline training complete.")

    def predict(self, code: str) -> Dict[str, float]:
        X = self.vectorizer.transform([code])
        proba = self.clf.predict_proba(X)[0]
        return {lbl: float(p) for lbl, p in zip(LABEL_NAMES, proba)}

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"vectorizer": self.vectorizer, "mlb": self.mlb, "clf": self.clf}, f)
        logger.info(f"Baseline model saved to {path}")

    @classmethod
    def load(cls, path: str) -> "BaselineModel":
        with open(path, "rb") as f:
            data = pickle.load(f)
        obj = cls.__new__(cls)
        obj.vectorizer = data["vectorizer"]
        obj.mlb = data["mlb"]
        obj.clf = data["clf"]
        return obj
