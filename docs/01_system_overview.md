


# ✍️  system_overview.md

```md
# 🧠 System Overview

## 📌 What is PolyGuard?

PolyGuard is a hybrid AI + static analysis system designed to detect security vulnerabilities in source code.

---

## 🧩 Core Components

### 1. Machine Learning Model
- Based on CodeBERT
- Detects vulnerability patterns

### 2. Rule Engine
- Detects known issues like SQLi, XSS

### 3. Scoring System
- Converts model output into:
  - Score (0–10)
  - Risk level

### 4. API Layer
- Built using FastAPI
- Handles requests and responses



## 🔄 Data Flow

-User Code
↓
-API
↓
-AI Model
↓
-Rule Engine
↓
-Scoring
↓
-Final Result


## 🌐 Tools Used

- Google Colab → training
- Google Drive → storage
- HuggingFace → model hosting
- GitHub → code repository


## 🎯 Goal

To provide fast, accurate, and explainable security analysis for developers.

