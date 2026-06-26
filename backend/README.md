# AI Voice Interview Coach Backend

FastAPI service for adaptive AI mock interviews using Gemini 2.5 Flash.

## Local Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Required environment variable:

```env
GEMINI_API_KEY=your_gemini_key
GEMINI_MODEL=gemini-2.5-flash
```

## API

- `GET /api/health`
- `GET /api/interview-types`
- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/sessions/{session_id}/answers`
- `POST /api/sessions/{session_id}/complete`
