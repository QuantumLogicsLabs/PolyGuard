"""
tokenizer.py
============
Tokenizes code snippets using the CodeBERT tokenizer.
"""
from transformers import RobertaTokenizer
from src.utils import get_logger

logger = get_logger(__name__)

_tokenizer = None


def get_tokenizer(model_name: str = "microsoft/codebert-base") -> RobertaTokenizer:
    global _tokenizer
    if _tokenizer is None:
        logger.info(f"Loading tokenizer: {model_name}")
        _tokenizer = RobertaTokenizer.from_pretrained(model_name)
    return _tokenizer


def tokenize_code(code: str, max_length: int = 512, model_name: str = "microsoft/codebert-base"):
    """
    Tokenize a code snippet.

    Returns a dict with input_ids, attention_mask tensors.
    """
    tokenizer = get_tokenizer(model_name)
    return tokenizer(
        code,
        max_length=max_length,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
