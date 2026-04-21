# ⚙️ Pipeline Explained

This document explains the complete workflow of PolyGuard — from raw data to a live API.

---

## 🔄 Full Pipeline Overview
Data → Cleaning → Training → Scoring → API → User


---

## 📥 Step 1 — Data Collection

- Data is collected from sources like:
  - CodeXGLUE
  - CodeSearchNet
- Contains labeled code (vulnerable / clean)

---

## 🧹 Step 2 — Data Cleaning

- Remove duplicate code
- Remove very short snippets
- Rename columns to simple format
- Save cleaned dataset as `train.csv`

---

## 🧠 Step 3 — Model Training

- Use CodeBERT (pre-trained model)
- Fine-tune on cleaned dataset
- Binary classification:
  - 0 = Clean
  - 1 = Vulnerable

---

## 📊 Step 4 — Scoring System

- Model outputs probabilities
- Converted into:
  - Score (0–10)
  - Confidence (%)
  - Verdict (CLEAN / VULNERABLE)

---

## 🌐 Step 5 — API Deployment

- FastAPI server handles requests
- User sends code
- API returns:
  - Score
  - Risk level
  - Suggestions

---

## 🎯 Final Output

PolyGuard provides:

- Security verdict
- Vulnerability type
- Fix suggestions
- Confidence scores

---

## 📌 Summary

PolyGuard pipeline transforms raw code data into a real-time security analysis system using AI and rule-based techniques.
