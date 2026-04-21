🏗️ System Architecture

This document describes how different components of PolyGuard work together.

## 📌 Overview

PolyGuard follows a hybrid architecture combining machine learning and rule-based analysis to detect vulnerabilities in code.

## 🧱 Components
1. Frontend
 Built with React
 Allows users to input code and view results
2. Backend API
 Built with FastAPI
 Handles requests and returns responses
3. ML Engine
 CodeBERT-based model
 Performs vulnerability classification
4. Rule Engine
 Detects known patterns (SQLi, XSS, etc.)
 Storage (Optional)
 Stores logs and results

## 🔄 Data Flow
User → Frontend → API → ML Model + Rules → Response → User

## ⚙️ Hybrid Approach

ML model detects patterns
Rule engine detects exact known issues
Combined for better accuracy

## 🔚 Summary

PolyGuard is modular and scalable, allowing independent development of each component.