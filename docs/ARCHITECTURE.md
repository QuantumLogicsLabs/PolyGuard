# PolyGuard — Architecture

## Overview

PolyGuard uses a **hybrid engine** that fuses two complementary approaches:

1. **Rules Engine** — regex + AST-based static analysis. Zero-shot, fast, high precision on well-known patterns (SQLi, XSS, memory safety, hardcoded secrets, weak crypto).
2. **ML Classifier** — CodeBERT fine-tuned multi-label classifier. Catches semantic vulnerabilities the rules engine misses.

Results from both are fused at inference time — if both flag the same vulnerability type, confidence is boosted and the finding is marked `source: fusion`.

---

## Component Map

```
src/
├── data_pipeline/
│   ├── dataset_builder.py   # Raw → processed splits (train/val/test JSON)
│   ├── code_dataset.py      # PyTorch Dataset with multi-hot label encoding
│   └── tokenizer.py         # CodeBERT tokenizer wrapper
│
├── models/
│   ├── codebert_classifier.py  # CodeBERT + linear head (multi-label)
│   └── baseline_model.py       # TF-IDF + LightGBM baseline
│
├── rules_engine/
│   ├── base_detector.py         # Abstract base + RuleFinding dataclass
│   ├── sqli_detector.py         # SQL Injection patterns
│   ├── xss_detector.py          # XSS patterns (JS/TS/HTML)
│   ├── memory_safety_detector.py # C/C++ memory safety
│   ├── secrets_detector.py      # Hardcoded credentials
│   ├── crypto_detector.py       # Weak cryptography
│   └── rules_engine.py          # Orchestrator
│
├── training/
│   ├── train.py             # CodeBERT training loop
│   └── train_baseline.py    # Baseline training
│
├── evaluation/
│   └── evaluator.py         # Metrics: precision, recall, F1, Hamming loss
│
├── inference/
│   ├── pipeline.py          # PolyGuardPipeline — public API
│   └── api.py               # FastAPI REST server
│
└── utils/
    ├── logger.py            # Structured logging
    └── config_loader.py     # YAML config loading
```

---

## Inference Flow

```
analyze(code, language)
    │
    ├── rules_engine.run_rules(code, language)
    │       ├── SQLiDetector.detect()
    │       ├── XSSDetector.detect()
    │       ├── MemorySafetyDetector.detect()
    │       ├── SecretsDetector.detect()
    │       └── CryptoDetector.detect()
    │
    ├── CodeBERTClassifier.forward()   ← if model is loaded
    │       └── sigmoid(linear(CLS embedding))
    │           → probability per label
    │
    └── _fuse(rule_findings, ml_findings)
            → deduplicate + boost confidence
            → sort by severity
            → compute overall_risk
```

---

## Label Schema

| ID | Name              | Severity | CWE     |
|----|-------------------|----------|---------|
| 0  | sql_injection     | Critical | CWE-89  |
| 1  | xss               | High     | CWE-79  |
| 2  | buffer_overflow   | Critical | CWE-120 |
| 3  | hardcoded_secret  | High     | CWE-798 |
| 4  | weak_crypto       | Medium   | CWE-327 |
| 5  | broken_auth       | High     | CWE-287 |

---

## Extending PolyGuard

### Adding a new rule detector

1. Create `src/rules_engine/my_detector.py` subclassing `BaseDetector`
2. Implement `detect(self, code, language) -> List[RuleFinding]`
3. Import and add an instance to `_DETECTORS` in `rules_engine.py`

### Adding a new vulnerability label

1. Add entry to `data/labels/vulnerability_types.json`
2. Add the label name to `LABEL_NAMES` in `code_dataset.py`
3. Update `NUM_LABELS` in `codebert_classifier.py`
4. Add metadata entry to `_LABEL_META` in `pipeline.py`
5. Re-train the model
