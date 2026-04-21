# 📘 Beginner Guide

## 🧠 What is PolyGuard?

PolyGuard is an AI-powered tool that scans your code and detects security vulnerabilities — similar to a spell checker, but for security issues.

It supports languages like Python, JavaScript, and C++.



## 🚨 What Problems Does It Detect?

PolyGuard can detect:

- SQL Injection
- Cross-Site Scripting (XSS)
- Hardcoded secrets (API keys, passwords)
- Memory issues (C/C++)
- Weak cryptography



## ⚙️ How Does It Work?

PolyGuard uses two techniques together:

### 1. AI Model (CodeBERT)
- Learns patterns from vulnerable code
- Flags suspicious code

### 2. Rule-Based Engine
- Detects known patterns (e.g., unsafe SQL queries)

👉 These two are combined to improve accuracy.



## 📊 What Do You Get?

For each issue, PolyGuard returns:

- Severity (Low / Medium / High)
- Code location
- Suggested fix
- Confidence score


## 👨‍💻 Who Should Use It?

- Developers
- Students learning secure coding
- Security engineers



## 💡 Example

```python
query = "SELECT * FROM users WHERE id = " + user_input
