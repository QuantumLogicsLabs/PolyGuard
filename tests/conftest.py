"""
conftest.py
===========
Shared pytest fixtures and configuration.
"""
import json
import os
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def synthetic_samples():
    return [
        {"code": 'cursor.execute("SELECT * FROM users WHERE id = " + uid)', "language": "python", "labels": ["sql_injection"]},
        {"code": "div.innerHTML = userInput;", "language": "javascript", "labels": ["xss"]},
        {"code": "strcpy(buf, argv[1]);", "language": "cpp", "labels": ["buffer_overflow"]},
        {"code": 'api_key = "sk-supersecretkey12345678"', "language": "python", "labels": ["hardcoded_secret"]},
        {"code": "hashlib.md5(data).hexdigest()", "language": "python", "labels": ["weak_crypto"]},
        {"code": "cursor.execute('SELECT * FROM t WHERE id = %s', (uid,))", "language": "python", "labels": []},
        {"code": "element.textContent = userInput;", "language": "javascript", "labels": []},
    ]


@pytest.fixture(scope="session")
def tmp_data_dir(synthetic_samples):
    """Write synthetic samples to a temp dir and return its path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        raw_dir = Path(tmpdir) / "raw"
        raw_dir.mkdir()
        with open(raw_dir / "samples.json", "w") as f:
            json.dump(synthetic_samples, f)
        yield tmpdir


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests that download models or need GPU")
