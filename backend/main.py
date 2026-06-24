from fastapi import FastAPI
from fastapi import UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.retriever import build_database, get_reference
from backend.interviewer import evaluate_answer
from backend.session import InterviewSession
from backend.feedback import generate_feedback
from backend.stt import transcribe_audio
from backend.tts import generate_speech

app = FastAPI(
    title="Voice Interview Agent"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session = InterviewSession()


@app.on_event("startup")
def startup():

    build_database()


@app.get("/")
def home():

    return {
        "message": "Voice Interview Agent Backend Running"
    }


@app.get("/start")
def start_interview():

    session.reset()

    current_question = session.get_current_question()

    return {
        "status": "started",
        "question_number": 1,
        "total_questions": len(session.questions),
        "question": current_question["question"],
        "domain": current_question["domain"]
    }


@app.post("/answer")
def answer(candidate_answer: str):

    current_question = session.get_current_question()

    if current_question is None:

        return {
            "status": "completed",
            "feedback": generate_feedback(
                session.history
            )
        }

    reference = get_reference(
        current_question["question"]
    )

    evaluation = evaluate_answer(
        question=reference["question"],
        ideal_answer=reference["ideal_answer"],
        key_points=reference["key_points"],
        conversation_history=session.current_conversation,
        latest_answer=candidate_answer,
        follow_up_count=session.follow_up_count
    )

    session.add_conversation(
        candidate_answer=candidate_answer,
        interviewer_response=evaluation.get(
            "follow_up",
            ""
        )
    )

    if (
        not evaluation.get("move_next", False)
        and session.follow_up_count < 2
        and evaluation.get("follow_up", "")
    ):

        return {
            "status": "follow_up",
            "feedback": evaluation["feedback"],
            "question": evaluation["follow_up"],
            "scores": {
                "technical": evaluation["technical_score"],
                "communication": evaluation["communication_score"],
                "confidence": evaluation["confidence_score"],
                "overall": evaluation["overall_score"]
            }
        }

    session.complete_question(
        evaluation
    )

    session.next_question()

    if session.is_finished():

        final_feedback = generate_feedback(
            session.get_history()
        )

        return {
            "status": "completed",
            "feedback": final_feedback
        }

    next_question = session.get_current_question()

    return {
        "status": "next_question",
        "question_number": session.current_index + 1,
        "total_questions": len(session.questions),
        "domain": next_question["domain"],
        "question": next_question["question"],
        "feedback": evaluation["feedback"],
        "scores": {
            "technical": evaluation["technical_score"],
            "communication": evaluation["communication_score"],
            "confidence": evaluation["confidence_score"],
            "overall": evaluation["overall_score"]
        }
    }


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):

    audio_path = f"recordings/{file.filename}"

    with open(audio_path, "wb") as buffer:
        buffer.write(await file.read())

    transcript = transcribe_audio(audio_path)

    return {
        "transcript": transcript
    }


@app.post("/speak")
def speak(text: str):

    audio_file = generate_speech(text)

    return FileResponse(
        audio_file,
        media_type="audio/mpeg",
        filename="response.mp3"
    )