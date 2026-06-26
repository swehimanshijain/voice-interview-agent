# AI Voice Interview Coach

# Working Steps
Landing Page: Display two interview types: 
1. HR Interview
2. Technical Interview (SDE)

When a user selects an interview type and clicks Start Interview: 
1. AI greets the user.
2. AI asks the first question.
3. Question is displayed on screen.
4. Question is spoken aloud using text-to-speech.
5. User clicks Start Recording.
6. Live speech transcription appears while speaking.
7. User clicks Stop Recording.
8. Answer is automatically submitted.
9. Evaluation happens immediately.
10. AI decides whether: Answer is good → next question
                        Answer is incomplete → follow-up question
                        User still struggles → coaching hint Repeat until interview completion.

    
## Database Design

The project uses `dataset/interview_knowledge_base.json` as JSON database.

```json
{
  "interview_types": {
    "technical_sde": {
      "label": "Technical Interview (SDE)",
      "opening": "Greeting text",
      "topics": [
        {
          "id": "oop",
          "name": "Object-Oriented Programming",
          "competencies": ["encapsulation", "abstraction"],
          "seed_question_intents": ["Ask about design principles."],
          "evaluation_rubric": "How strong answers should be judged."
        }
      ]
    }
  }
}
```

Runtime session state is in memory and tracks session id, interview type, shuffled topic order, current question, already asked questions, follow-up attempts, answer transcripts, evaluations, coaching hints, and aggregate scores. For persistence, replace the in-memory dictionary in `backend/app/services/session_manager.py` with SQLite using the same session model.

## API Design

- `GET /api/health` - service health check
- `GET /api/interview-types` - list HR and Technical SDE interview options
- `POST /api/sessions` - create a new adaptive interview session
- `GET /api/sessions/{session_id}` - fetch current session state
- `POST /api/sessions/{session_id}/answers` - submit transcript, evaluate, and receive follow-up/coaching/next question
- `POST /api/sessions/{session_id}/complete` - generate final performance report

## Folder Structure

```text
voice-interview-agent/
  backend/
    app/
      config.py
      knowledge_base.py
      schemas.py
      services/
        gemini_service.py
        session_manager.py
    main.py
    requirements.txt
  dataset/
    interview_knowledge_base.json
  frontend/
    src/
      components/
      hooks/
      services/
      styles/
      App.jsx
      main.jsx
    package.json
    vite.config.js
```

## Local Development

Backend:

```bash
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Set `GEMINI_API_KEY` in `.env`. The frontend uses browser-native speech recognition and text-to-speech.
