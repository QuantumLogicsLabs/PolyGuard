import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# load model directly from HuggingFace Hub - no Drive needed
MODEL_NAME = "YOUR_HF_USERNAME/polyguard-model"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()

suggestions = {
    "sqli": "Use parameterized queries instead of building SQL strings manually.",
    "xss": "Sanitize all user inputs before rendering them to the page.",
    "secrets": "Never hardcode API keys or passwords. Use environment variables instead.",
    "crypto": "Avoid MD5 and SHA1. Use SHA256 or bcrypt for hashing.",
    "memory": "Always check buffer sizes before copying data in C/C++.",
    "auth": "Always verify user permissions before returning sensitive data.",
}

language_tips = {
    "python": [
        "Use list comprehensions instead of for loops where possible.",
        "Use f-strings for string formatting instead of .format() or %.",
        "Use 'with open()' for file handling instead of open/close.",
    ],
    "javascript": [
        "Use const and let instead of var.",
        "Use async/await instead of nested callbacks.",
        "Always use === instead of == for comparisons.",
    ],
    "java": [
        "Use try-with-resources for handling streams and connections.",
        "Use StringBuilder instead of String concatenation in loops.",
    ],
    "go": [
        "Always handle errors explicitly.",
        "Use goroutines for concurrency instead of threads.",
    ],
}

app = FastAPI(title="PolyGuard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str
    language: str = "python"


@app.get("/")
def home():
    return {"status": "PolyGuard API is running"}


@app.post("/analyze")
def analyze(request: CodeRequest):
    inputs = tokenizer(
        request.code, return_tensors="pt", truncation=True, max_length=256, padding=True
    )
    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.softmax(outputs.logits, dim=1)
    clean_conf = probs[0][0].item()
    vuln_conf = probs[0][1].item()
    score = round(clean_conf * 10, 1)

    if score >= 8:
        risk = "low"
    elif score >= 5:
        risk = "medium"
    else:
        risk = "high"

    findings = []
    if vuln_conf > 0.4:
        findings.append(suggestions["sqli"])
    if vuln_conf > 0.6:
        findings.append(suggestions["xss"])

    tips = language_tips.get(request.language.lower(), ["Keep learning!"])

    return {
        "score": score,
        "risk": risk,
        "verdict": "CLEAN" if score >= 7 else "VULNERABLE",
        "clean_confidence": round(clean_conf * 100, 1),
        "vuln_confidence": round(vuln_conf * 100, 1),
        "findings": findings,
        "tips": tips,
    }
