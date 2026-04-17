<div align="center">

# 🛡️ PolyGuard

### AI-Powered Code Security Analyzer

_Hybrid ML + Static Analysis for Vulnerability Detection across C++, JavaScript, and Python_

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange)]()

</div>

---

## 📖 Overview

**PolyGuard** is an open-source AI code security analyzer that combines machine learning with static analysis to detect, score, and fix security vulnerabilities in source code. Think of it as a lightweight, self-hostable alternative to GitHub Advanced Security — built for developers who want real-time, explainable security feedback without vendor lock-in.

PolyGuard is designed as both a research platform and a production-ready tool. It exposes a clean inference API, supports multi-language analysis (C++, JavaScript, Python), and is architected to scale into a full SaaS product or GitHub App.

> **QuantumLogics Project** — Part of the broader vision to build startup-grade security tooling from first principles.

---

## ✨ Key Features

| Feature                        | Description                                                            |
| ------------------------------ | ---------------------------------------------------------------------- |
| 🔍 **Vulnerability Detection** | Detects SQLi, XSS, buffer overflows, hardcoded secrets, and more       |
| 🤖 **AI Fix Generation**       | Suggests secure code rewrites using a fine-tuned transformer model     |
| 📊 **Risk Scoring**            | Assigns severity (Low / Medium / High / Critical) per finding          |
| 🌐 **Web Dashboard**           | Upload a repo or paste code — see issues, fixes, and confidence scores |
| 🔌 **GitHub Integration**      | Auto-scans PRs and comments inline on vulnerabilities                  |
| 🧠 **Hybrid Engine**           | ML classifier + rule-based static analyzer fused at inference time     |
| 🌍 **Multi-language**          | Single unified model for C++, JavaScript, and Python                   |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│         Code upload · Issue viewer · Fix suggestions        │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP / WebSocket
┌───────────────────────────▼─────────────────────────────────┐
│                    Backend API (FastAPI)                      │
│              Auth · Queue dispatch · REST routes             │
└──────┬──────────────────────────────────────────┬───────────┘
       │ Celery + Redis                            │
┌──────▼───────────────────┐        ┌─────────────▼───────────┐
│      ML Engine           │        │    Static Analyzer       │
│  CodeBERT embeddings     │        │  AST parsing (Tree-sitter│
│  Multi-label classifier  │        │  Rule-based detectors    │
│  Confidence scoring      │        │  SQLi · XSS · Mem-safety │
└──────────────┬───────────┘        └──────────────┬──────────┘
               │                                   │
               └──────────────┬────────────────────┘
                              │ Fusion layer
                    ┌─────────▼──────────┐
                    │   MongoDB          │
                    │  Results · History │
                    │  Audit logs        │
                    └────────────────────┘
```

The core inference entrypoint is `src/inference/pipeline.py`. Everything else — training, feature extraction, rule compilation — is internal to the ML system and not exposed externally.

---

## 🗂️ Project Structure

```
PolyGuard/
├── configs/                    # YAML configs for model, training, paths
├── data/
│   ├── raw/                    # CVE dataset, OWASP samples, GitHub vulns
│   ├── processed/              # train / val / test splits (JSON)
│   └── labels/                 # Vulnerability type taxonomy
├── notebooks/                  # EDA, baseline experiments, analysis
├── src/
│   ├── data_pipeline/          # Collection, cleaning, tokenization
│   ├── features/               # Code embeddings, AST parsing
│   ├── models/                 # Baseline, transformer, multi-label classifier
│   ├── rules_engine/           # SQLi, XSS, memory safety rule detectors
│   ├── training/               # Train loop, loss functions, metrics
│   ├── evaluation/             # Eval scripts, confusion matrix, error analysis
│   ├── inference/              # ← Public API: pipeline.py
│   └── utils/                  # Logger, config loader, helpers
├── tests/                      # Unit tests for pipeline, model, rules, inference
├── experiments/                # Isolated experiment folders (no overwriting)
│   ├── exp_01_baseline_tfidf/
│   ├── exp_02_codebert/
│   └── exp_03_hybrid_model/
├── models_saved/               # Serialized model artifacts
├── scripts/                    # Shell scripts for train / eval / infer
└── docs/                       # Architecture, dataset guide, model report
```

---

## ⚡ Execution Flow

```
Step 1 — Data Pipeline
  data/raw/ ──► collector.py ──► cleaner.py ──► dataset_builder.py
                                                        │
Step 2 — Feature Extraction                             ▼
  tokenizer.py ──► embedding.py ──► ast_parser.py ──► code_representation.py
                                                        │
Step 3 — Model Training                                 ▼
  train.py ──► trainer.py ──► loss_functions.py ──► models_saved/
                                                        │
Step 4 — Rule Engine                                    ▼
  sql_injection_rules.py + xss_rules.py + memory_safety_rules.py
                                                        │
Step 5 — Inference                                      ▼
  src/inference/pipeline.py  ◄──── ML output + Rules output (fused)
```

---

## 🔬 ML Approaches

### Baseline

- TF-IDF features on code tokens
- Logistic Regression / LightGBM classifier
- Fast to train, useful as a performance floor

### Primary Model (CodeBERT)

- Pre-trained on code from GitHub across 6 languages
- Fine-tuned on CVE and SARD vulnerability datasets
- Multi-label output (a snippet can have multiple vulnerability types)
- Confidence scores per label for risk ranking

### Advanced (Planned)

- **Graph Neural Networks**: Convert code → AST → Program Dependency Graph → GNN classifier. Captures control/data flow patterns that token-level models miss.
- **Fusion Layer**: Weighted combination of ML confidence + rule engine match score for final verdict.

---

## 🧪 Datasets

| Source                                              | Description                                                                      |
| --------------------------------------------------- | -------------------------------------------------------------------------------- |
| [SARD](https://samate.nist.gov/SARD/)               | NIST Software Assurance Reference Dataset — labeled vulnerable/safe C, C++, Java |
| [CVE Details](https://www.cvedetails.com/)          | Real-world CVE examples with exploit code                                        |
| [OWASP WebGoat](https://github.com/WebGoat/WebGoat) | Intentionally vulnerable web app samples                                         |
| GitHub Vulnerable Repos                             | Scraped and labeled via CodeQL advisories                                        |

All datasets are normalized into `data/processed/train.json`, `val.json`, `test.json` using `src/data_pipeline/dataset_builder.py`.

---

## 🚀 Quickstart

### Prerequisites

- Python 3.10+
- CUDA-capable GPU (recommended for training; CPU works for inference)
- Redis (for async task queue)
- MongoDB (for result storage)

### Installation

```bash
git clone https://github.com/your-org/polyguard.git
cd polyguard
pip install -r requirements.txt
pip install -e .
```

### Configuration

Edit `configs/paths.yaml` to point to your data directories, then:

```bash
cp configs/model_config.yaml configs/model_config.local.yaml
# Edit model_config.local.yaml with your hyperparameters
```

### Run the Full Pipeline

```bash
# 1. Preprocess data
bash scripts/preprocess.sh

# 2. Train the model
bash scripts/train.sh

# 3. Evaluate
bash scripts/evaluate.sh

# 4. Run inference on a file
bash scripts/run_inference.sh --input path/to/your/code.py
```

### Python API

```python
from src.inference.pipeline import PolyGuardPipeline

pipeline = PolyGuardPipeline.from_pretrained("models_saved/best_model.pt")

results = pipeline.analyze("""
import sqlite3
query = "SELECT * FROM users WHERE id = " + user_input
""", language="python")

for finding in results.findings:
    print(f"[{finding.severity}] {finding.vuln_type} at line {finding.line}")
    print(f"  Fix: {finding.suggested_fix}")
    print(f"  Confidence: {finding.confidence:.1%}")
```

---

## 🧩 Tech Stack

| Layer               | Technology                             |
| ------------------- | -------------------------------------- |
| ML Framework        | PyTorch 2.x + HuggingFace Transformers |
| Code Embeddings     | CodeBERT (`microsoft/codebert-base`)   |
| AST Parsing         | Tree-sitter (multi-language)           |
| Backend API         | FastAPI + Uvicorn                      |
| Task Queue          | Celery + Redis                         |
| Database            | MongoDB (results), SQLite (local dev)  |
| Frontend            | React + Tailwind CSS                   |
| Deployment          | Docker + AWS ECS / EC2                 |
| Experiment Tracking | MLflow (planned)                       |

---

## 🔌 GitHub Integration

PolyGuard can be installed as a GitHub App to automatically scan pull requests:

1. Set up a webhook pointing to your PolyGuard backend
2. Configure `GITHUB_APP_ID` and `GITHUB_PRIVATE_KEY` in your environment
3. PolyGuard will comment inline on any PR diff lines containing detected vulnerabilities

> Full setup guide: [`docs/api_spec_future.md`](docs/api_spec_future.md)

---

## 📊 Vulnerability Types Detected

| Category          | Examples                                                |
| ----------------- | ------------------------------------------------------- |
| **Injection**     | SQL Injection, Command Injection, LDAP Injection        |
| **XSS**           | Reflected XSS, Stored XSS, DOM-based XSS                |
| **Memory Safety** | Buffer overflow, use-after-free, null dereference       |
| **Secrets**       | Hardcoded API keys, passwords, tokens                   |
| **Cryptography**  | Weak algorithms (MD5/SHA1), insecure random             |
| **Auth**          | Broken access control, insecure direct object reference |

Label taxonomy is defined in `data/labels/vulnerability_types.json`.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_data_pipeline.py
pytest tests/test_rules_engine.py
pytest tests/test_model.py
pytest tests/test_inference.py
```

---

## 📈 Experiments

Each experiment lives in its own isolated directory under `experiments/` — no files are overwritten between runs.

| Experiment              | Approach            | Status         |
| ----------------------- | ------------------- | -------------- |
| `exp_01_baseline_tfidf` | TF-IDF + LightGBM   | ✅ Complete    |
| `exp_02_codebert`       | CodeBERT fine-tuned | 🔄 In Progress |
| `exp_03_hybrid_model`   | ML + Rules fusion   | 🗓️ Planned     |

Logs are in `experiments/logs/`. Results are tracked in `docs/model_report.md`.

---

## 🗺️ Roadmap

- [x] Project architecture and data pipeline
- [x] Rule-based static analysis engine (SQLi, XSS, memory safety)
- [ ] CodeBERT fine-tuning on SARD + CVE dataset
- [ ] Multi-label classifier with confidence scoring
- [ ] Web dashboard (React)
- [ ] FastAPI backend with async inference
- [ ] GitHub PR integration
- [ ] GNN-based vulnerability detection
- [ ] Chrome extension / VS Code plugin
- [ ] SaaS deployment on AWS

---

## 📚 Documentation

- [`docs/architecture.md`](docs/architecture.md) — Detailed system design
- [`docs/dataset_guide.md`](docs/dataset_guide.md) — Dataset collection and labeling process
- [`docs/model_report.md`](docs/model_report.md) — Experiment results and model comparisons
- [`docs/api_spec_future.md`](docs/api_spec_future.md) — Planned REST API specification

---

## 🤝 Contributing

Contributions are welcome. Please open an issue to discuss your idea before submitting a PR. All contributions must include tests and pass the existing test suite.

```bash
# Before submitting
pytest tests/ -v
flake8 src/ --max-line-length=100
```

---

## 📄 License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

<div align="center">

Built with 🔐 by the QuantumLogics team.

_PolyGuard — Secure code is not optional._

</div>
