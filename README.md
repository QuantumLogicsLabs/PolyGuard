<div align="center">

# 🛡️ PolyGuard

### AI-Powered Code Security Analyzer

_Hybrid ML + Static Analysis for Vulnerability Detection across C++, JavaScript, and Python_

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Spaces-FFD21E?logo=huggingface)](https://huggingface.co/spaces/MUHAMMADSAADAMIN/polyguard-space)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-orange)]()

</div>

---

## 📖 Overview

**PolyGuard** is an open-source AI code security analyzer that combines machine learning with static analysis to detect, score, and fix security vulnerabilities in source code. Think of it as a lightweight, self-hostable alternative to GitHub Advanced Security — built for developers who want real-time, explainable security feedback without vendor lock-in.

PolyGuard is designed as both a research platform and a production-ready tool. It exposes a clean inference API, supports multi-language analysis (C++, JavaScript, Python, and more), and is architected to scale into a full SaaS product or GitHub App.

> **QuantumLogics Project** — Part of the broader vision to build startup-grade security tooling from first principles.

---

## ✨ Key Features

| Feature | Description |
| --- | --- |
| 🔍 **Vulnerability Detection** | Detects SQLi, XSS, buffer overflows, hardcoded secrets, and 50+ more |
| 🤖 **AI Fix Generation** | Suggests secure code rewrites using a fine-tuned transformer model |
| 📊 **Risk Scoring** | Assigns a 0–10 safety score and severity (Low / Medium / High) per finding |
| 🌐 **Live Web API** | Free, no sign-up — send code, get results back in under 500ms |
| 🔌 **GitHub Integration** | Auto-scans PRs and comments inline on vulnerabilities |
| 🧠 **Hybrid Engine** | ML classifier + rule-based static analyzer fused at inference time |
| 🌍 **Multi-language** | Supports Python, JavaScript, C, C++, Java, PHP, Ruby, and Go |

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

## ☁️ Infrastructure & Toolchain

PolyGuard is built entirely on free, open tools stitched together into a production pipeline:

| Tool | Role |
| --- | --- |
| **Google Colab** | GPU-powered training environment |
| **Google Drive** | Persistent storage for datasets and model artifacts |
| **HuggingFace Hub** | Model hosting — [`MUHAMMADSAADAMIN/polyguard-model`](https://huggingface.co/MUHAMMADSAADAMIN/polyguard-model) |
| **HuggingFace Spaces** | Live API hosting — [`polyguard-space`](https://huggingface.co/spaces/MUHAMMADSAADAMIN/polyguard-space) |
| **GitHub** | Source code repository and collaboration |


```



## 🗂️ Project Structure

```
PolyGuard/
├── configs/                    # YAML configs for model, training, paths
├── data/
│   ├── raw/                    # CVE dataset, OWASP samples, GitHub vulns
│   ├── processed/              # train / val / test splits (JSON)
│   └── labels/                 # Vulnerability type taxonomy
├── notebooks/                  # The 5 pipeline notebooks (01–05)
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

## 🔬 ML Approaches

### Baseline

- TF-IDF features on code tokens
- Logistic Regression / LightGBM classifier
- Fast to train, useful as a performance floor

### Primary Model (CodeBERT)

- Pre-trained on code from GitHub across 6 languages (`microsoft/codebert-base`)
- Fine-tuned on CodeXGLUE and SARD vulnerability datasets
- Binary classification output: `clean` vs `vulnerable`
- Confidence scores per label used for risk ranking

**Training settings:**

| Hyperparameter | Value |
| --- | --- |
| Epochs | 3 |
| Batch size | 8 |
| Max token length | 256 |
| Warmup steps | 100 |
| Weight decay | 0.01 |
| Eval strategy | Per epoch |

### Advanced (Planned)

- **Graph Neural Networks:** Convert code → AST → Program Dependency Graph → GNN classifier. Captures control/data flow patterns that token-level models miss.
- **Multi-label classifier:** Detect multiple vulnerability types simultaneously with per-label confidence scores.
- **Fusion Layer:** Weighted combination of ML confidence + rule engine match score for final verdict.

---

## 📊 Scoring & Output

For every code snippet analyzed, PolyGuard returns:

| Field | Description |
| --- | --- |
| `score` | Safety score 0–10 (higher = safer) |
| `risk` | `low` / `medium` / `high` |
| `verdict` | `CLEAN` or `VULNERABLE` |
| `clean_confidence` | Model's % confidence the code is safe |
| `vuln_confidence` | Model's % confidence the code is dangerous |
| `findings` | List of actionable fix suggestions |
| `tips` | Language-specific best practices |

**Score thresholds:**

```
≥ 8.0  →  LOW risk     →  CLEAN
5.0–7.9 →  MEDIUM risk  →  VULNERABLE
< 5.0  →  HIGH risk    →  VULNERABLE
```

**Example response (vulnerable code):**

```json
{
  "score": 2.3,
  "risk": "high",
  "verdict": "VULNERABLE",
  "clean_confidence": 23.0,
  "vuln_confidence": 77.0,
  "findings": [
    "Use parameterized queries instead of building SQL strings manually.",
    "Sanitize all user inputs before rendering them to the page."
  ],
  "tips": [
    "Use list comprehensions instead of for loops where possible.",
    "Use f-strings for string formatting."
  ]
}
```

---

## 🧪 Datasets

| Source | Description |
| --- | --- |
| [CodeXGLUE — Defect Detection](https://huggingface.co/datasets/google/code_x_glue_cc_defect_detection) | Labeled vulnerable/safe C code from NIST |
| [CodeSearchNet](https://huggingface.co/datasets/code_search_net) | Large Python code corpus from GitHub (5,000 examples used) |
| [SARD](https://samate.nist.gov/SARD/) | NIST Software Assurance Reference Dataset |
| [CVE Details](https://www.cvedetails.com/) | Real-world CVE examples with exploit code |
| [OWASP WebGoat](https://github.com/WebGoat/WebGoat) | Intentionally vulnerable web app samples |

All datasets are normalized into `data/processed/train.json`, `val.json`, `test.json` using `src/data_pipeline/dataset_builder.py`.

---

## 📦 Model Deployment

The trained model is published to HuggingFace for permanent, public access:

**Model repo:** `MUHAMMADSAADAMIN/polyguard-model`

```python
from transformers import AutoModelForSequenceClassification, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("MUHAMMADSAADAMIN/polyguard-model")
model = AutoModelForSequenceClassification.from_pretrained("MUHAMMADSAADAMIN/polyguard-model")
```

**Live demo (HuggingFace Spaces):** `MUHAMMADSAADAMIN/polyguard-space`

The Space runs a Gradio interface backed by the same model. It auto-installs dependencies from `requirements.txt` and loads the model from the Hub on startup.

**To retrain and redeploy:**

1. Add more labeled examples to the dataset (doubling data can improve accuracy by 5–15%)
2. Run `03_train_model.ipynb` on GPU (20–40 minutes)
3. Push new model weights to HuggingFace Hub
4. Restart the HuggingFace Space (takes 3–5 minutes)
5. Verify by sending the same test code and comparing confidence scores

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

```bash
# Edit configs/paths.yaml to point to your data directories
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

### REST API

```bash
# POST to the live endpoint
curl -X POST https://<your-space>.hf.space/analyze \
  -H "Content-Type: application/json" \
  -d '{"code": "query = \"SELECT * FROM users WHERE id = \" + user_input", "language": "python"}'
```

---

## 📊 Vulnerability Types Detected

| Category | Examples |
| --- | --- |
| **Injection** | SQL Injection, Command Injection, LDAP Injection |
| **XSS** | Reflected XSS, Stored XSS, DOM-based XSS |
| **Memory Safety** | Buffer overflow, use-after-free, null dereference |
| **Secrets** | Hardcoded API keys, passwords, tokens |
| **Cryptography** | Weak algorithms (MD5/SHA1), insecure random |
| **Auth** | Broken access control, insecure direct object reference |

Label taxonomy is defined in `data/labels/vulnerability_types.json`.

---

## 🧩 Tech Stack

| Layer | Technology |
| --- | --- |
| ML Framework | PyTorch 2.x + HuggingFace Transformers |
| Code Embeddings | CodeBERT (`microsoft/codebert-base`) |
| AST Parsing | Tree-sitter (multi-language) |
| Backend API | FastAPI + Uvicorn |
| Task Queue | Celery + Redis |
| Database | MongoDB (results), SQLite (local dev) |
| Frontend | React + Tailwind CSS |
| Model Hosting | HuggingFace Hub + Spaces |
| Experiment Tracking | MLflow (planned) |
| Deployment | Docker + AWS ECS / EC2 |

---

## 📈 Experiments

Each experiment lives in its own isolated directory under `experiments/` — no files are overwritten between runs.

| Experiment | Approach | Status |
| --- | --- | --- |
| `exp_01_baseline_tfidf` | TF-IDF + LightGBM | ✅ Complete |
| `exp_02_codebert` | CodeBERT fine-tuned | 🔄 In Progress |
| `exp_03_hybrid_model` | ML + Rules fusion | 🗓️ Planned |

Logs are in `experiments/logs/`. Results are tracked in `docs/model_report.md`.

---

## 🗺️ Roadmap

### Current State ✅
- AI model trained and deployed (HuggingFace Hub)
- Live API running — free, no sign-up
- Website with real-time scanning
- Rule-based static analysis engine (SQLi, XSS, memory safety)
- Supports 8 programming languages

### Phase 1 — Better Training Data
- Download 10x more labeled vulnerable code samples
- Add language-specific vulnerability patterns
- Introduce severity levels (Critical / High / Medium / Low) instead of binary labels

### Phase 2 — Better AI Architecture
- Multi-label classifier: detect multiple vulnerability types simultaneously
- Line-level localization: point to the exact line instead of flagging the whole file
- Map findings to CWE identifiers (e.g. CWE-89 for SQL Injection)

### Phase 3 — Better Suggestions
- Use a code-generation model (e.g. CodeLlama) to write corrected code automatically
- Combine ML detection with rule-based checks for improved accuracy
- Generate natural language explanations of why something is dangerous

### Phase 4 — Production Ready
- GPU-backed inference for sub-500ms responses
- Response caching for repeated scans
- Bulk scanning: analyze 50+ files at once for CI/CD integration
- Chrome extension / VS Code plugin
- SaaS deployment on AWS

---

## 🔌 GitHub Integration

PolyGuard can be installed as a GitHub App to automatically scan pull requests:

1. Set up a webhook pointing to your PolyGuard backend
2. Configure `GITHUB_APP_ID` and `GITHUB_PRIVATE_KEY` in your environment
3. PolyGuard will comment inline on any PR diff lines containing detected vulnerabilities

> Full setup guide: [`docs/api_spec_future.md`](docs/api_spec_future.md)

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