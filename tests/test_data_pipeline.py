"""
tests/test_data_pipeline.py
===========================
Unit tests for the data pipeline.
"""
import json
import tempfile
import os
import pytest

from src.data_pipeline.dataset_builder import (
    validate_sample,
    build_splits,
    _generate_synthetic_samples,
    load_raw_samples,
)


def test_validate_sample_valid():
    sample = {"code": "x = 1", "language": "python", "labels": []}
    assert validate_sample(sample) is True


def test_validate_sample_missing_field():
    sample = {"code": "x = 1", "language": "python"}
    assert validate_sample(sample) is False


def test_build_splits_ratios():
    samples = [
        {"code": f"code_{i}", "language": "python", "labels": []}
        for i in range(100)
    ]
    splits = build_splits(samples, train_ratio=0.8, val_ratio=0.1)
    assert len(splits["train"]) == 80
    assert len(splits["val"]) == 10
    assert len(splits["test"]) == 10


def test_build_splits_no_overlap():
    samples = [
        {"code": f"code_{i}", "language": "python", "labels": []}
        for i in range(50)
    ]
    splits = build_splits(samples)
    all_codes = (
        [s["code"] for s in splits["train"]]
        + [s["code"] for s in splits["val"]]
        + [s["code"] for s in splits["test"]]
    )
    assert len(all_codes) == len(set(all_codes))


def test_synthetic_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        _generate_synthetic_samples(tmpdir)
        loaded = load_raw_samples(tmpdir)
        assert len(loaded) > 0
        for s in loaded:
            assert "code" in s
            assert "language" in s
            assert "labels" in s


def test_split_reproducibility():
    samples = [
        {"code": f"code_{i}", "language": "python", "labels": []}
        for i in range(100)
    ]
    s1 = build_splits(samples, seed=42)
    s2 = build_splits(samples, seed=42)
    assert [x["code"] for x in s1["train"]] == [x["code"] for x in s2["train"]]
