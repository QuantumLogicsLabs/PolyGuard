# PolyGuard — Dataset Guide

## Supported Data Sources

| Source | Type | Labels |
|--------|------|--------|
| SARD (NIST) | C/C++ vulnerable functions | buffer_overflow, etc. |
| CVE Details | Multi-language real CVEs | All categories |
| OWASP WebGoat | JS/Java web vulns | sql_injection, xss |
| GitHub advisories | Python, JS | All categories |
| Synthetic (built-in) | All languages | All categories |

---

## Data Format

Each sample in `data/raw/*.json` must follow this schema:

```json
{
  "code": "cursor.execute('SELECT * FROM users WHERE id = ' + uid)",
  "language": "python",
  "labels": ["sql_injection"],
  "source": "synthetic"
}
```

- `code`: raw source code string (any length; will be truncated to `max_seq_length` tokens)
- `language`: one of `python`, `javascript`, `cpp`, `c`, `typescript`
- `labels`: list of label names from the taxonomy; empty list `[]` means safe/clean
- `source`: origin of the sample (for provenance tracking)

---

## Running the Pipeline

```bash
# 1. Place raw JSON files in data/raw/
# 2. Run preprocessing to create train/val/test splits
python -m src.data_pipeline.dataset_builder

# Or via script:
bash scripts/preprocess.sh
```

Outputs:
- `data/processed/train.json` — 80% of samples
- `data/processed/val.json`   — 10% of samples
- `data/processed/test.json`  — 10% of samples

---

## Synthetic Data (Demo Mode)

If `data/raw/` is empty, the dataset builder automatically generates 160 synthetic samples covering all 6 vulnerability types plus clean samples. This is enough to smoke-test the pipeline end-to-end, but **not** sufficient for a production-quality model — real labeled data is required for that.

---

## Class Imbalance

Vulnerability datasets are typically imbalanced (far more clean samples than vulnerable ones). Strategies implemented or planned:

- **Oversampling**: repeat minority-class samples in training
- **Loss weighting**: `BCEWithLogitsLoss(pos_weight=...)` in the trainer
- **Threshold tuning**: choose per-label thresholds on the validation set to maximize F1
