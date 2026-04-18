"""
codebert_classifier.py
======================
Multi-label vulnerability classifier built on top of CodeBERT.
"""
import torch
import torch.nn as nn
from transformers import RobertaModel
from typing import Optional

NUM_LABELS = 6


class CodeBERTClassifier(nn.Module):
    """
    CodeBERT-based multi-label classifier for vulnerability detection.

    Architecture:
        CodeBERT [CLS] embedding → Dropout → Linear → Sigmoid
    """

    def __init__(
        self,
        model_name: str = "microsoft/codebert-base",
        num_labels: int = NUM_LABELS,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.encoder = RobertaModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size  # 768
        self.dropout = nn.Dropout(dropout)
        self.classifier = nn.Linear(hidden_size, num_labels)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor,
        labels: Optional[torch.Tensor] = None,
    ):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]  # [CLS] token
        cls_output = self.dropout(cls_output)
        logits = self.classifier(cls_output)
        probs = torch.sigmoid(logits)

        loss = None
        if labels is not None:
            loss_fn = nn.BCEWithLogitsLoss()
            loss = loss_fn(logits, labels)

        return {"loss": loss, "logits": logits, "probs": probs}

    def save(self, path: str) -> None:
        torch.save(self.state_dict(), path)

    @classmethod
    def load(cls, path: str, **kwargs) -> "CodeBERTClassifier":
        model = cls(**kwargs)
        model.load_state_dict(torch.load(path, map_location="cpu"))
        model.eval()
        return model
