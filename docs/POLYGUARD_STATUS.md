# PolyGuard — Project Status (Plain-English Explainer)

> **File purpose:** A simple, honest snapshot of what this project *is*, what
> *actually works today*, and what is *still missing or inconsistent*. Written
> so a non-expert (or a new contributor) can understand it in a few minutes.
>
> Last reviewed: 2026-06-28

---

## 1. What is PolyGuard, in one sentence?

PolyGuard is an **AI code security scanner**: you give it a chunk of source
code, and it tells you whether the code looks **safe or vulnerable**, gives it a
**risk score (0–10)**, and suggests **fixes** (e.g. "use parameterized queries
instead of building SQL strings").

Think of it as a free, self-hostable mini version of GitHub Advanced Security.

---

## 2. How it works (the simple mental model)

There are **two brains** working together:

1. **A rule-based scanner** (`src/rules_engine/`) — hand-written pattern
   detectors for known bad code: SQL injection, XSS, hardcoded secrets, weak
   crypto (MD5/SHA1), and C/C++ memory-safety issues. Fast and predictable.

2. **A machine-learning model** (CodeBERT, fine-tuned) — reads the code the way
   a human-ish AI would and predicts whether it's vulnerable. Catches things the
   rules miss.

The intended design is to **fuse** the two: if both flag the same problem,
confidence goes up. This fusion logic lives in
[`src/inference/pipeline.py`](../src/inference/pipeline.py).

### The pieces, end to end

| Piece | Where | What it does |
| --- | --- | --- |
| Training notebooks | `notebooks/01`–`05` | Collect data → clean → train the model → score → serve |
| Trained model | `models_saved/PolyGuard/` | The actual fine-tuned CodeBERT weights (`model.safetensors`) |
| Model hosting | HuggingFace Hub | Permanent public copy of the model |
| Live API | HuggingFace Spaces ([`app.py`](../app.py)) | A FastAPI server that loads the model and answers `POST /analyze` |
| Website | `website/` | A React site that lets you paste code and calls the live API |
| Local library | `src/` | The "real" hybrid engine (rules + ML + fusion) for self-hosting |

---

## 3. What actually works today ✅

- **A model is trained and saved.** `models_saved/PolyGuard/` contains real
  weights. Metadata says: trained 2026-04-29, ~16.7k training samples, **best F1
  ≈ 0.67**, 14 epochs, version `v5_extended`.
- **A live web API exists** ([`app.py`](../app.py)) — a FastAPI `/analyze`
  endpoint hosted on HuggingFace Spaces
  (`muhammadsaadamin-polyguard-api.hf.space`).
- **A working website** (`website/`, React + Vite) that posts code to that API
  and renders a score, verdict, findings, and tips. The Analyzer page is wired
  to the real endpoint.
- **A full local rules engine** — five real detectors (SQLi, XSS, memory safety,
  secrets, crypto) under `src/rules_engine/`, orchestrated by `run_rules()`.
- **A clean hybrid pipeline** (`src/inference/pipeline.py`) with rules + ML +
  fusion, line/severity/CWE-aware `Finding` objects, and a `rules_only()` mode
  for running with no model.
- **Tests, configs, scripts, and docs** are all scaffolded and present.

---

## 4. What is missing, broken, or inconsistent ⚠️

This is the honest part. The repo *looks* more finished than it is, mostly
because the **deployed product and the local codebase disagree with each other.**

### 4.1 The deployed model and the local code expect *different models*

This is the biggest issue.

- The **saved/deployed model** is a **binary classifier** — its
  `config.json` says `single_label_classification` with 2 outputs
  (`clean` vs `vulnerable`). The live [`app.py`](../app.py) treats it that way:
  it only produces a clean/vuln confidence and then *guesses* "maybe SQLi / maybe
  XSS" from fixed probability thresholds — it does **not** actually identify the
  vulnerability type.
- The **local hybrid pipeline** (`src/inference/pipeline.py` +
  `configs/model_config.yaml`) expects a **6-label multi-label model**
  (`sql_injection`, `xss`, `buffer_overflow`, `hardcoded_secret`, `weak_crypto`,
  `broken_auth`).

**Result:** the polished multi-label engine in `src/` cannot run against the
model that's actually deployed. One of the two needs to be brought in line with
the other (most likely: retrain as true multi-label, or downgrade the pipeline
expectation to binary).

### 4.2 `app.py` has a placeholder username

[`app.py` line 8](../app.py#L8) still says `MODEL_NAME = "YOUR_HF_USERNAME/polyguard-model"`.
The deployed Space presumably has the real value, but the committed file would
not run as-is. Should be `MUHAMMADSAADAMIN/...`.

### 4.3 The live API is "ML-only" — the rules engine isn't deployed

All the careful rule detectors and the fusion logic live in `src/` but the public
`app.py` doesn't import or use any of them. So the live product is **weaker** than
the local library: no line-level findings, no CWE mapping, no real vuln-type
detection, no fusion. Endpoints the website advertises (`/analyze_batch`,
`/health`) are not in the committed `app.py` either.

### 4.4 Datasets are not in the repo

`data/` only contains `.gitkeep` and the label taxonomy. The `raw/processed/`
splits the README describes are absent (expected — they're large/built by the
notebooks), but it means the project **cannot be reproduced from a fresh clone**
without re-running data collection.

### 4.5 Model quality is modest

F1 ≈ 0.67 on a binary task is a usable proof-of-concept, not production-grade.
The README's "detects 50+ vulnerability types" and "8 languages" claims are
**aspirational** — the actual model is binary, and real type/line detection comes
only from the (un-deployed) rules engine.

### 4.6 Roadmap items that are claimed but not built

From the README/roadmap, still **not done**: multi-label classifier, line-level
localization in the ML path, CWE mapping in deployment, AI fix *generation*
(CodeLlama-style rewriting — current "fixes" are static canned strings), GitHub
App integration (config keys exist in `.env.example` but no webhook handler),
MongoDB/Redis/Celery infra (referenced in the architecture diagram but not wired
into the running API), batch scanning, and any IDE/Chrome extension.

### 4.7 Minor housekeeping

- `models_saved/PolyGuard/` is a **nested git repo** (an HF clone, includes its
  own `.git` and `.git/lfs`) sitting inside the main repo and currently untracked
  — this should be a submodule, gitignored, or pulled at runtime, not committed.
- File is named per request **POLYMENTOR**_STATUS.md, but the project is called
  **PolyGuard** everywhere else. (Flagging in case "PolyMentor" was meant to be a
  different/renamed product.)

---

## 5. The honest one-paragraph summary

PolyGuard is a **working end-to-end demo**: a real fine-tuned model, a live API,
and a polished website that genuinely scans pasted code. But under the hood the
**deployed product is a simple binary "safe vs vulnerable" classifier**, while
the repository's much more sophisticated **multi-label hybrid engine (rules + ML
+ fusion) is built but not actually deployed and expects a model that doesn't
exist yet.** The top priority to make the project "real" is to **reconcile those
two halves** — train a true multi-label model and serve the full `src/` pipeline
(rules + fusion) through `app.py` — and then deliver the roadmap features that are
currently described as if finished but aren't.

---

## 6. Suggested next steps (in priority order)

1. **Decide the model contract:** binary or 6-label multi-label, and make
   `config.yaml`, `pipeline.py`, the trained model, and `app.py` all agree.
2. **Deploy the real engine:** have `app.py` call `PolyGuardPipeline` (rules +
   ML + fusion) instead of a bare softmax, so the live API matches the docs.
3. **Fix `app.py` placeholder** model name and add the advertised `/health` and
   `/analyze_batch` endpoints (or remove them from the website).
4. **Make the model honest:** update README claims to match reality, or retrain
   to actually meet them. Add line-level + CWE output to the ML path.
5. **Clean up `models_saved/PolyGuard/`** (submodule / gitignore / runtime pull).
6. **Add a reproducible data path** so a fresh clone can rebuild the datasets.
