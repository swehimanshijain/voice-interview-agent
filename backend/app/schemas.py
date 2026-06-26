from typing import Literal

from pydantic import BaseModel, Field


InterviewType = Literal["hr", "technical_sde"]
QuestionKind = Literal["main", "follow_up"]
NextAction = Literal["answer", "coaching", "completed"]


class InterviewTypeInfo(BaseModel):
    id: InterviewType
    label: str
    description: str


class Topic(BaseModel):
    id: str
    name: str
    competencies: list[str]
    seed_question_intents: list[str]
    evaluation_rubric: str


class QuestionTurn(BaseModel):
    id: str
    kind: QuestionKind
    topic_id: str
    topic_name: str
    question: str
    expected_concepts: list[str] = Field(default_factory=list)
    difficulty: str = "medium"


class EvaluationResult(BaseModel):
    score: int = Field(ge=0, le=10)
    relevance: int = Field(ge=0, le=10)
    accuracy: int = Field(ge=0, le=10)
    completeness: int = Field(ge=0, le=10)
    confidence: int = Field(ge=0, le=10)
    communication: int = Field(ge=0, le=10)
    strengths: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    follow_up_required: bool = False
    coaching_required: bool = False
    feedback: str


class SessionCreateRequest(BaseModel):
    interview_type: InterviewType


class AnswerRequest(BaseModel):
    transcript: str = Field(min_length=1)


class ScoreSnapshot(BaseModel):
    overall: int
    technical: int
    communication: int
    confidence: int


class SessionResponse(BaseModel):
    session_id: str
    interview_type: InterviewType
    greeting: str
    question_number: int
    max_questions: int
    current_question: QuestionTurn | None
    next_action: NextAction
    coaching_hint: str | None = None
    latest_evaluation: EvaluationResult | None = None
    scores: ScoreSnapshot | None = None


class AnswerResponse(SessionResponse):
    status: Literal["follow_up", "next_question", "coaching", "completed"]


class FinalReport(BaseModel):
    overall_score: int
    technical_score: int
    communication_score: int
    confidence_score: int
    strengths: list[str]
    areas_to_improve: list[str]
    personalized_feedback: str
    interview_summary: str


class CompleteResponse(BaseModel):
    session_id: str
    report: FinalReport
