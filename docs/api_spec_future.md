# PolyGuard — REST API Specification

Base URL: `http://localhost:8000`

---

## Endpoints

### `GET /health`
Returns API status.

**Response**
```json
{ "status": "ok", "version": "0.1.0" }
```

---

### `POST /scan`
Full hybrid scan (rules + ML model).

**Request**
```json
{
  "code": "cursor.execute(\"SELECT * FROM users WHERE id = \" + uid)",
  "language": "python"
}
```

**Response**
```json
{
  "language": "python",
  "overall_risk": "Critical",
  "finding_count": 1,
  "scan_time_ms": 312.4,
  "findings": [
    {
      "vuln_type": "sql_injection",
      "severity": "Critical",
      "line": 1,
      "column": 1,
      "snippet": "cursor.execute(\"SELECT * FROM users WHERE id = \" +",
      "message": "Possible SQL Injection: user-controlled data concatenated into SQL query.",
      "cwe": "CWE-89",
      "confidence": 0.92,
      "suggested_fix": "Use parameterized queries / prepared statements.",
      "source": "rules"
    }
  ]
}
```

---

### `POST /scan/rules-only`
Fast scan using only the static analysis rules engine. No ML model loaded.

Same request/response shape as `/scan`.

---

## Supported Languages

| Value | Description |
|-------|-------------|
| `python` | Python 3.x |
| `javascript` | JavaScript / Node.js |
| `typescript` | TypeScript |
| `cpp` | C++ |
| `c` | C |

---

## Interactive Docs

When the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
