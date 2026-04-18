"""
tests/test_model.py
===================
Tests for the ML model classes. Uses small mock tensors — no GPU required.
"""
import pytest
import torch
from src.models.codebert_classifier import CodeBERTClassifier, NUM_LABELS


@pytest.mark.slow  # skip with: pytest -m "not slow"
def test_model_forward_pass():
    """Full forward pass with CodeBERT (downloads model on first run)."""
    model = CodeBERTClassifier(num_labels=NUM_LABELS)
    model.eval()
    batch_size, seq_len = 2, 64
    input_ids      = torch.randint(0, 1000, (batch_size, seq_len))
    attention_mask = torch.ones(batch_size, seq_len, dtype=torch.long)
    with torch.no_grad():
        out = model(input_ids=input_ids, attention_mask=attention_mask)
    assert out["probs"].shape == (batch_size, NUM_LABELS)
    assert torch.all(out["probs"] >= 0) and torch.all(out["probs"] <= 1)


@pytest.mark.slow
def test_model_loss_computed_with_labels():
    model = CodeBERTClassifier(num_labels=NUM_LABELS)
    model.eval()
    input_ids      = torch.randint(0, 1000, (1, 64))
    attention_mask = torch.ones(1, 64, dtype=torch.long)
    labels         = torch.zeros(1, NUM_LABELS)
    labels[0][0]   = 1.0  # sql_injection
    with torch.no_grad():
        out = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
    assert out["loss"] is not None
    assert out["loss"].item() > 0
