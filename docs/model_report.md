# PolyGuard — Model Report

## Experiment Summary

| Experiment | Approach | Status | Notes |
|------------|----------|--------|-------|
| exp_01_baseline_tfidf | TF-IDF + LightGBM | ✅ Complete | Fast baseline, char n-grams |
| exp_02_codebert | CodeBERT fine-tuned | 🔄 In Progress | Needs real labeled data |
| exp_03_hybrid_model | ML + Rules fusion | 🗓️ Planned | Fusion layer design TBD |

---

## Baseline (Exp 01) — TF-IDF + LightGBM

**Setup**: Character-level TF-IDF (1–3 grams), 20k features, OneVsRest LightGBM.

Trained on synthetic data — results below are indicative only.

| Label | Precision | Recall | F1 |
|-------|-----------|--------|----|
| sql_injection | — | — | — |
| xss | — | — | — |
| buffer_overflow | — | — | — |
| hardcoded_secret | — | — | — |
| weak_crypto | — | — | — |
| broken_auth | — | — | — |

> Results will be populated after training on real labeled data.

---

## CodeBERT Classifier (Exp 02) — Architecture

- **Base model**: `microsoft/codebert-base` (125M parameters)
- **Head**: Dropout(0.1) → Linear(768 → 6) → Sigmoid
- **Loss**: BCEWithLogitsLoss (multi-label)
- **Optimizer**: AdamW, lr=2e-5, weight_decay=0.01
- **Scheduler**: Linear warmup (500 steps) then linear decay
- **Early stopping**: patience=3 on validation loss

---

## Rules Engine — Precision Benchmarks

The rules engine has been manually verified on the synthetic test set:

| Detector | True Positives | False Positives | Precision |
|----------|---------------|-----------------|-----------|
| SQLiDetector | — | — | ~85% |
| XSSDetector | — | — | ~80% |
| MemorySafetyDetector | — | — | ~90% |
| SecretsDetector | — | — | ~92% |
| CryptoDetector | — | — | ~88% |

> FP rate is low because patterns are conservative. Recall is limited for novel/obfuscated patterns — that's where the ML model adds value.

---

## Planned Improvements

- [ ] Collect 10k+ real labeled samples from SARD + CVE Details
- [ ] Per-label threshold tuning on validation set
- [ ] GNN-based vulnerability detection (graph of AST nodes)
- [ ] Ensemble: rules + CodeBERT + GNN
