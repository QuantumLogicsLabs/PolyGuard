# 📓 Notebooks Guide



## 🧱 Overall Flow
Notebook 01 → Data Collection
Notebook 02 → Data Cleaning
Notebook 03 → Model Training
Notebook 04 → Scoring
Notebook 05 → API

---

## 📥 Notebook 01 — Data Collection

- Downloads datasets from HuggingFace
- Sources:
  - CodeXGLUE
  - CodeSearchNet
- Produces raw dataset

---

## 🧹 Notebook 02 — Data Cleaning

- Removes duplicates
- Filters short code snippets
- Renames columns
- Saves clean data as `train.csv`

---

## 🧠 Notebook 03 — Model Training

- Loads cleaned dataset
- Uses CodeBERT model
- Fine-tunes for vulnerability detection
- Saves trained model

---

## 📊 Notebook 04 — Scorer

- Loads trained model
- Converts predictions into:
  - Score (0–10)
  - Risk level
  - Suggestions

---

## 🌐 Notebook 05 — API

- Wraps model into FastAPI
- Exposes `/analyze` endpoint
- Allows real-time code scanning

---

## 🎯 Purpose of This Structure

- Modular development
- Easy debugging
- Clear workflow separation

---

## 📌 Summary

Each notebook represents one stage of the PolyGuard pipeline, making the system easy to understand, modify, and improve.

