# CareerOS AI Backend

FastAPI backend scaffold for CareerOS AI.

## Local development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`
