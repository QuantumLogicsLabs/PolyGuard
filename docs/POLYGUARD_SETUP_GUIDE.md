# PolyGuard — Step-by-Step Setup & Run Guide

> This guide gets you from zero to a running scanner in four stages:
> **Setup → Data → Train → Run**

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|-------------|----------------|-------|
| Python | 3.10+ | `python --version` |
| pip | Latest | `pip install --upgrade pip` |
| Git | Any | For version control |
| RAM | 8 GB | 16 GB recommended for CodeBERT training |
| GPU (optional) | CUDA-capable | CPU works for inference; GPU needed for fast training |

---

## Stage 1 — Project Setup

### 1.1 Unzip and enter the project

```bash
unzip PolyGuard.zip
cd PolyGuard
```

### 1.2 Create a virtual environment

**Windows (Command Prompt):**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 1.3 Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> ⏳ This takes 3–10 minutes. PyTorch and Transformers are large packages.
> If you have a CUDA GPU, install the CUDA-enabled PyTorch first:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```

### 1.4 Install PolyGuard as a local package

```bash
pip install -e .
```

This lets Python resolve `from src.inference.pipeline import ...` from anywhere inside the project.

### 1.5 Verify the install

```bash
python -c "from src.inference.pipeline import PolyGuardPipeline; print('✅ Install OK')"
```

---

## Stage 2 — Run Tests (No Model Needed)

Run the full test suite in **rules-only mode** — no GPU, no model download required:

```bash
pytest tests/ -v -m "not slow"
```

Expected output:
```
tests/test_rules_engine.py::test_sqli_detected_string_concat_python  PASSED
tests/test_rules_engine.py::test_xss_innerhtml_variable              PASSED
tests/test_rules_engine.py::test_hardcoded_api_key                   PASSED
tests/test_inference.py::test_pipeline_detects_sqli                  PASSED
tests/test_api.py::test_health_endpoint                              PASSED
... (all PASSED)
```

> If all tests pass, your setup is correct.

---

## Stage 3 — Quick Scan (Rules Engine, Instant)

You can scan code **right now** without training any model.

### 3a — Scan inline code

```bash
python quick_scan.py --code 'cursor.execute("SELECT * FROM users WHERE id = " + uid)' --language python
```

Expected output:
```
══════════════════════════════════════════════════════════
  PolyGuard Security Scan
  Source   : <inline>
  Language : python
  Risk     : Critical
  Time     : 1.2 ms
══════════════════════════════════════════════════════════

  [1] [Critical] SQL_INJECTION  —  Line 1  (confidence: 85%)  [rules]
       Possible SQL Injection: user-controlled data concatenated into SQL query.
       CWE: CWE-89
       Fix: Use parameterized queries / prepared statements. ...
```

### 3b — Scan a file

```bash
python quick_scan.py --file path/to/your/code.py --language python
```

### 3c — Scan JavaScript or C++

```bash
python quick_scan.py --file app.js --language javascript
python quick_scan.py --file main.cpp --language cpp
```

### 3d — Start the API server (rules-only)

```bash
uvicorn src.inference.api:app --reload --host 0.0.0.0 --port 8000
```

Then open **http://localhost:8000/docs** in your browser — you get a full Swagger UI.

**Test it with curl:**
```bash
curl -X POST http://localhost:8000/scan/rules-only \
  -H "Content-Type: application/json" \
  -d '{"code": "api_key = \"sk-supersecretvalue\"", "language": "python"}'
```

---

## Stage 4 — Train the ML Model (Optional, Improves Accuracy)

The rules engine works without any training. If you want the full hybrid ML+rules pipeline, follow these steps.

### 4.1 Prepare data

**Option A — Use synthetic demo data (fastest, for testing only):**
```bash
python -m src.data_pipeline.dataset_builder
```
This auto-generates 160 synthetic labeled samples and writes `data/processed/train.json`, `val.json`, `test.json`.

**Option B — Use real data (recommended for production quality):**

1. Download labeled samples from any of these sources:
   - [SARD (NIST)](https://samate.nist.gov/SARD/) — C/C++ vulnerable functions
   - [OWASP WebGoat](https://github.com/WebGoat/WebGoat) — web vulnerability samples
   - [CVE Details](https://www.cvedetails.com/) — real-world CVEs

2. Format each sample as JSON:
   ```json
   {
     "code": "your source code here",
     "language": "python",
     "labels": ["sql_injection"],
     "source": "sard"
   }
   ```

3. Place JSON files in `data/raw/` and run:
   ```bash
   python -m src.data_pipeline.dataset_builder
   ```

### 4.2 Train the baseline (fast, 2–5 minutes on CPU)

```bash
python -m src.training.train_baseline
```

Output: `models_saved/baseline_tfidf.pkl`

### 4.3 Train the CodeBERT classifier (slow, GPU recommended)

> ⚠️ First run downloads `microsoft/codebert-base` (~500 MB). Needs ~6 GB RAM minimum.

```bash
python -m src.training.train
```

Training progress is logged to `experiments/logs/train.log`.
Best model is saved to `models_saved/best_model.pt` whenever validation loss improves.

**To monitor progress live:**
```bash
tail -f experiments/logs/train.log
```

**Typical training time:**
| Hardware | Time per epoch (synthetic data) |
|----------|--------------------------------|
| CPU only | ~5–15 min |
| RTX 3080 | ~30 sec |
| Google Colab (T4) | ~2 min |

### 4.4 Evaluate the model

```bash
python -m src.evaluation.evaluator
```

Prints per-label precision, recall, F1, Hamming loss, and Jaccard score.

### 4.5 Run the full hybrid pipeline with ML model

```bash
python quick_scan.py --file path/to/your/code.py --use-model
```

Or via the API (automatically loads the model):
```bash
uvicorn src.inference.api:app --reload
# then POST to /scan (not /scan/rules-only)
```

---

## Directory Reference

```
PolyGuard/
├── configs/                  # YAML configs (model, paths, API)
├── data/
│   ├── raw/                  # Place your raw labeled samples here
│   ├── processed/            # train/val/test.json (auto-generated)
│   └── labels/               # Vulnerability taxonomy JSON
├── docs/                     # Architecture, dataset guide, API spec
├── experiments/              # Per-experiment configs and logs
├── models_saved/             # Trained model checkpoints
├── scripts/                  # Shell scripts for each pipeline step
├── src/
│   ├── data_pipeline/        # Dataset builder, tokenizer, Dataset class
│   ├── models/               # CodeBERT classifier, baseline model
│   ├── rules_engine/         # Static analysis detectors
│   ├── training/             # Training loops
│   ├── evaluation/           # Metrics and evaluation scripts
│   ├── inference/            # pipeline.py (public API), api.py (FastAPI)
│   └── utils/                # Logger, config loader
├── tests/                    # pytest test suite
├── quick_scan.py             # Top-level CLI scanner
├── setup.py                  # pip install -e .
└── requirements.txt
```

---

## Cheat Sheet — Common Commands

```bash
# Activate environment (run first every session)
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# Quick scan (no model needed)
python quick_scan.py --file my_code.py

# Run tests
pytest tests/ -v -m "not slow"

# Build dataset (generates synthetic data if raw/ is empty)
python -m src.data_pipeline.dataset_builder

# Train baseline (fast, CPU)
python -m src.training.train_baseline

# Train CodeBERT classifier (slow, GPU recommended)
python -m src.training.train

# Evaluate
python -m src.evaluation.evaluator

# Start API server
uvicorn src.inference.api:app --reload --port 8000
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: src` | Run `pip install -e .` from the project root |
| `FileNotFoundError: configs/model_config.yaml` | Make sure you're running commands from inside the `PolyGuard/` directory |
| `CUDA out of memory` | Reduce `batch_size` in `configs/model_config.yaml` (try 4 or 8) |
| `Model not found at models_saved/best_model.pt` | Train first (`python -m src.training.train`), or use `--rules-only` flag |
| `Connection refused` on API | Make sure uvicorn is running; check port 8000 is not blocked by firewall |
| Slow tokenizer download | First run downloads CodeBERT tokenizer (~500 MB); subsequent runs use cache |

---

## Next Steps

- Add real labeled samples to `data/raw/` for production-quality detection
- Tune thresholds in `configs/model_config.yaml` → `inference.threshold`
- Add a new detector by subclassing `BaseDetector` in `src/rules_engine/`
- Read `docs/architecture.md` for a full component breakdown
