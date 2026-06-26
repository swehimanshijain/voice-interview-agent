import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from backend.app.knowledge_base import KnowledgeBase
from backend.app.schemas import (
    AnswerResponse,
    CompleteResponse,
    EvaluationResult,
    FinalReport,
    InterviewType,
    QuestionTurn,
    ScoreSnapshot,
    SessionResponse,
)
from backend.app.services.gemini_service import GeminiService


@dataclass
class CompletedTurn:
    question: QuestionTurn
    answer: str
    evaluation: EvaluationResult


@dataclass
class InterviewSession:
    id: str
    interview_type: InterviewType
    greeting: str
    max_questions: int
    topics: list
    topic_index: int = 0
    main_question_count: int = 0
    current_question: QuestionTurn | None = None
    active_main_question: QuestionTurn | None = None
    follow_up_attempted: bool = False
    asked_questions: list[str] = field(default_factory=list)
    completed_turns: list[CompletedTurn] = field(default_factory=list)
    current_attempts: list[dict[str, Any]] = field(default_factory=list)
    latest_evaluation: EvaluationResult | None = None
    coaching_hint: str | None = None
    completed: bool = False


class SessionNotFoundError(KeyError):
    pass


class InterviewSessionManager:
    def __init__(self, kb: KnowledgeBase, ai: GeminiService, max_questions: int):
        self.kb = kb
        self.ai = ai
        self.max_questions = max_questions
        self.sessions: dict[str, InterviewSession] = {}

    def create(self, interview_type: InterviewType) -> SessionResponse:
        topics = self.kb.topics(interview_type)
        random.shuffle(topics)

        session = InterviewSession(
            id=str(uuid.uuid4()),
            interview_type=interview_type,
            greeting=self.kb.opening(interview_type),
            max_questions=self.max_questions,
            topics=topics,
        )
        self.sessions[session.id] = session
        self._advance_to_next_main_question(session)
        return self._to_session_response(session, next_action="answer")

    def get(self, session_id: str) -> SessionResponse:
        session = self._get_session(session_id)
        next_action = "completed" if session.completed else "answer"
        return self._to_session_response(session, next_action=next_action)

    def answer(self, session_id: str, transcript: str) -> AnswerResponse:
        session = self._get_session(session_id)
        if session.completed or session.current_question is None:
            return self._to_answer_response(session, status="completed", next_action="completed")

        topic = self._topic_by_id(session, session.current_question.topic_id)
        evaluation = self.ai.evaluate_answer(
            topic=topic,
            question=session.current_question,
            transcript=transcript,
            previous_attempts=session.current_attempts,
        )
        session.latest_evaluation = evaluation
        session.completed_turns.append(
            CompletedTurn(
                question=session.current_question,
                answer=transcript,
                evaluation=evaluation,
            )
        )
        session.current_attempts.append(
            {
                "question": session.current_question.question,
                "answer": transcript,
                "score": evaluation.score,
                "missing_concepts": evaluation.missing_concepts,
            }
        )

        should_follow_up = (
            evaluation.follow_up_required
            and not evaluation.coaching_required
            and not session.follow_up_attempted
            and evaluation.score < 8
        )
        if should_follow_up:
            follow_up = self.ai.generate_follow_up(
                topic=topic,
                current_question=session.active_main_question or session.current_question,
                answer=transcript,
                evaluation=evaluation,
                asked_questions=session.asked_questions,
            )
            follow_up.id = str(uuid.uuid4())
            session.current_question = follow_up
            session.follow_up_attempted = True
            session.asked_questions.append(follow_up.question)
            return self._to_answer_response(session, status="follow_up", next_action="answer")

        should_coach = (
            evaluation.coaching_required
            or evaluation.score < 6
            or (session.follow_up_attempted and evaluation.missing_concepts)
        )
        if should_coach:
            session.coaching_hint = self.ai.generate_coaching_hint(
                topic=topic,
                question=session.active_main_question or session.current_question,
                evaluation=evaluation,
            )
            self._advance_after_main_question(session)
            if session.completed:
                return self._to_answer_response(session, status="completed", next_action="completed")
            return self._to_answer_response(session, status="coaching", next_action="coaching")

        self._advance_after_main_question(session)
        if session.completed:
            return self._to_answer_response(session, status="completed", next_action="completed")
        return self._to_answer_response(session, status="next_question", next_action="answer")

    def complete(self, session_id: str) -> CompleteResponse:
        session = self._get_session(session_id)
        scores = self._aggregate_scores(session)
        report = self.ai.generate_report(
            interview_label=self._interview_label(session.interview_type),
            turns=[
                {
                    "topic": turn.question.topic_name,
                    "kind": turn.question.kind,
                    "question": turn.question.question,
                    "answer": turn.answer,
                    "evaluation": turn.evaluation.model_dump(),
                }
                for turn in session.completed_turns
            ],
            aggregate_scores=scores,
        )
        return CompleteResponse(session_id=session.id, report=report)

    def _advance_after_main_question(self, session: InterviewSession) -> None:
        session.current_attempts = []
        session.follow_up_attempted = False
        session.active_main_question = None

        if session.main_question_count >= session.max_questions:
            session.current_question = None
            session.completed = True
            return

        self._advance_to_next_main_question(session)

    def _advance_to_next_main_question(self, session: InterviewSession) -> None:
        if session.main_question_count >= session.max_questions:
            session.current_question = None
            session.completed = True
            return

        topic = self._next_topic(session)
        question = self.ai.generate_question(
            interview_label=self._interview_label(session.interview_type),
            topic=topic,
            asked_questions=session.asked_questions,
            recent_context=[
                {
                    "topic": turn.question.topic_name,
                    "question": turn.question.question,
                    "score": turn.evaluation.score,
                    "missing_concepts": turn.evaluation.missing_concepts,
                }
                for turn in session.completed_turns[-6:]
            ],
            question_number=session.main_question_count + 1,
        )
        question.id = str(uuid.uuid4())
        session.current_question = question
        session.active_main_question = question
        session.main_question_count += 1
        session.asked_questions.append(question.question)
        session.coaching_hint = None

    def _next_topic(self, session: InterviewSession):
        if session.topic_index >= len(session.topics):
            random.shuffle(session.topics)
            session.topic_index = 0
        topic = session.topics[session.topic_index]
        session.topic_index += 1
        return topic

    def _topic_by_id(self, session: InterviewSession, topic_id: str):
        for topic in session.topics:
            if topic.id == topic_id:
                return topic
        raise ValueError(f"Unknown topic id: {topic_id}")

    def _get_session(self, session_id: str) -> InterviewSession:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise SessionNotFoundError(session_id) from exc

    def _interview_label(self, interview_type: InterviewType) -> str:
        for item in self.kb.interview_types():
            if item.id == interview_type:
                return item.label
        return interview_type

    def _aggregate_scores(self, session: InterviewSession) -> dict[str, int]:
        if not session.completed_turns:
            return {
                "overall_score": 0,
                "technical_score": 0,
                "communication_score": 0,
                "confidence_score": 0,
            }
        evaluations = [turn.evaluation for turn in session.completed_turns]
        return {
            "overall_score": self._average_to_100([item.score for item in evaluations]),
            "technical_score": self._average_to_100(
                [
                    round((item.relevance + item.accuracy + item.completeness) / 3)
                    for item in evaluations
                ]
            ),
            "communication_score": self._average_to_100(
                [item.communication for item in evaluations]
            ),
            "confidence_score": self._average_to_100([item.confidence for item in evaluations]),
        }

    @staticmethod
    def _average_to_100(scores: list[int]) -> int:
        if not scores:
            return 0
        return round((sum(scores) / len(scores)) * 10)

    def _score_snapshot(self, session: InterviewSession) -> ScoreSnapshot | None:
        if not session.completed_turns:
            return None
        scores = self._aggregate_scores(session)
        return ScoreSnapshot(
            overall=scores["overall_score"],
            technical=scores["technical_score"],
            communication=scores["communication_score"],
            confidence=scores["confidence_score"],
        )

    def _to_session_response(
        self,
        session: InterviewSession,
        next_action: str,
    ) -> SessionResponse:
        return SessionResponse(
            session_id=session.id,
            interview_type=session.interview_type,
            greeting=session.greeting,
            question_number=min(session.main_question_count, session.max_questions),
            max_questions=session.max_questions,
            current_question=session.current_question,
            next_action=next_action,
            coaching_hint=session.coaching_hint,
            latest_evaluation=session.latest_evaluation,
            scores=self._score_snapshot(session),
        )

    def _to_answer_response(
        self,
        session: InterviewSession,
        status: str,
        next_action: str,
    ) -> AnswerResponse:
        base = self._to_session_response(session, next_action=next_action)
        return AnswerResponse(status=status, **base.model_dump())
