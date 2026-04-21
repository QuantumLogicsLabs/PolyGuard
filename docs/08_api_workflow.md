
# 🌐 API Workflow

This document explains how the PolyGuard API processes incoming code and returns a structured security analysis.

---

## 📌 Overview

PolyGuard exposes a REST API built using FastAPI. It allows users to submit source code and receive real-time vulnerability analysis powered by a machine learning model and supporting logic.

---

## 🔁 End-to-End Flow

1. A user sends code to the API via an HTTP request
2. The API validates the input
3. The code is tokenized and passed to the trained model
4. The model generates prediction probabilities
5. These probabilities are converted into a score and verdict
6. Suggestions and tips are added
7. A JSON response is returned to the user

---

## 📥 Input Format

The API expects a JSON request in the following format:

```json
{
  "code": "your source code here",
  "language": "python"
}
⚙️ Internal Processing
1. Tokenization
2. Model Inference
3. Probability Conversion
4. Score Calculation
5. Risk Classification
6. Verdict
Score ≥ 7 → CLEAN
Score < 7 → VULNERABLE

VULNERABLE
📤 Output Format
{
  "score": 2.3,
  "risk": "high",
  "verdict": "VULNERABLE",
  "clean_confidence": 23.0,
  "vuln_confidence": 77.0,
  "findings": [
    "Use parameterized queries instead of building SQL strings manually."
  ],
  "tips": [
    "Use 'with open()' for file handling.",
    "Use f-strings for string formatting."
  ]
}
🌍 Deployment

The API can be exposed using:

ngrok (for development)
HuggingFace Spaces (for production/demo)




