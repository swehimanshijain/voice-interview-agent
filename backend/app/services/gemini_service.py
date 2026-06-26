import json
import re
from typing import Any, TypeVar

import google.generativeai as genai
from pydantic import BaseModel, ValidationError

from backend.app.schemas import EvaluationResult, FinalReport, QuestionTurn, Topic

T = TypeVar("T", bound=BaseModel)


class AIResponseError(RuntimeError):
    """Raised when Gemini does not return valid structured output."""


class GeminiService:
    def __init__(self, api_key: str, model_name: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def generate_question(
        self,
        interview_label: str,
        topic: Topic,
        asked_questions: list[str],
        recent_context: list[dict[str, Any]],
        question_number: int,
    ) -> QuestionTurn:
        prompt = f"""
You are a senior interviewer creating one fresh interview question.

Interview type: {interview_label}
Question number: {question_number}
Topic: {topic.name}
Topic competencies: {topic.competencies}
Seed intents, for inspiration only: {topic.seed_question_intents}
Evaluation rubric: {topic.evaluation_rubric}
Already asked questions: {asked_questions}
Recent interview context: {recent_context[-4:]}

Rules:
- Generate a new question, not a repeat or close paraphrase of anything already asked.
- The question must be answerable by voice in 60-120 seconds.
- Do not include an ideal answer.
- Return JSON only.

JSON schema:
{{
  "id": "temporary",
  "kind": "main",
  "topic_id": "{topic.id}",
  "topic_name": "{topic.name}",
  "question": "string",
  "expected_concepts": ["concept 1", "concept 2"],
  "difficulty": "easy|medium|hard"
}}
"""
        result = self._generate_json(prompt, QuestionTurn)
        result.kind = "main"
        result.topic_id = topic.id
        result.topic_name = topic.name
        return result

    def generate_follow_up(
        self,
        topic: Topic,
        current_question: QuestionTurn,
        answer: str,
        evaluation: EvaluationResult,
        asked_questions: list[str],
    ) -> QuestionTurn:
        prompt = f"""
You are a professional interviewer asking one concise follow-up question.

Topic: {topic.name}
Competencies: {topic.competencies}
Original question: {current_question.question}
Candidate answer: {answer}
Missing concepts: {evaluation.missing_concepts}
Already asked questions: {asked_questions}

Rules:
- Ask only one question.
- Guide the candidate toward the missing concepts without revealing the ideal answer.
- Do not provide a full explanation or list the answer.
- Return JSON only.

JSON schema:
{{
  "id": "temporary",
  "kind": "follow_up",
  "topic_id": "{topic.id}",
  "topic_name": "{topic.name}",
  "question": "string",
  "expected_concepts": ["concept 1", "concept 2"],
  "difficulty": "{current_question.difficulty}"
}}
"""
        result = self._generate_json(prompt, QuestionTurn)
        result.kind = "follow_up"
        result.topic_id = topic.id
        result.topic_name = topic.name
        return result

    def evaluate_answer(
        self,
        topic: Topic,
        question: QuestionTurn,
        transcript: str,
        previous_attempts: list[dict[str, Any]],
    ) -> EvaluationResult:
        prompt = f"""
You are an expert interview evaluator.

Evaluate the candidate answer against the question and topic rubric.

Topic: {topic.name}
Competencies to look for: {topic.competencies}
Rubric: {topic.evaluation_rubric}
Question: {question.question}
Expected concepts: {question.expected_concepts}
Previous attempts for this main question: {previous_attempts}
Candidate transcript: {transcript}

Scoring:
- score, relevance, accuracy, completeness, confidence, and communication are integers 0-10.
- Confidence should be inferred from clarity, specificity, directness, and hedging in the transcript.

Follow-up and coaching policy:
- follow_up_required=true when the answer is relevant but incomplete and the candidate should be probed.
- coaching_required=true when the answer is weak, unrelated, or remains weak after a prior attempt.
- Never reveal a full ideal answer in feedback.
- Feedback must be 1-2 constructive sentences.

Return valid JSON only:
{{
  "score": 0,
  "relevance": 0,
  "accuracy": 0,
  "completeness": 0,
  "confidence": 0,
  "communication": 0,
  "strengths": [],
  "missing_concepts": [],
  "follow_up_required": false,
  "coaching_required": false,
  "feedback": "string"
}}
"""
        return self._generate_json(prompt, EvaluationResult)

    def generate_coaching_hint(
        self,
        topic: Topic,
        question: QuestionTurn,
        evaluation: EvaluationResult,
    ) -> str:
        prompt = f"""
You are coaching a candidate after a weak or incomplete answer.

Topic: {topic.name}
Question: {question.question}
Missing concepts: {evaluation.missing_concepts}

Write a short coaching hint that nudges the candidate toward better thinking.
Do not reveal the complete answer, do not list all concepts as the final answer, and do not sound like a lecture.
Return JSON only:
{{"hint": "string"}}
"""
        data = self._generate_raw_json(prompt)
        hint = str(data.get("hint", "")).strip()
        if not hint:
            raise AIResponseError("Gemini returned an empty coaching hint.")
        return hint

    def generate_report(
        self,
        interview_label: str,
        turns: list[dict[str, Any]],
        aggregate_scores: dict[str, int],
    ) -> FinalReport:
        prompt = f"""
You are an interview coach generating a final candidate scorecard.

Interview type: {interview_label}
Aggregate scores: {aggregate_scores}
Evaluated turns: {turns}

Requirements:
- Overall score is out of 100.
- Technical score is out of 100. For HR interviews, interpret it as role/readiness score.
- Communication and confidence scores are out of 100.
- Feedback should be specific, constructive, and not disclose ideal answers.
- Return JSON only.

JSON schema:
{{
  "overall_score": 0,
  "technical_score": 0,
  "communication_score": 0,
  "confidence_score": 0,
  "strengths": [],
  "areas_to_improve": [],
  "personalized_feedback": "string",
  "interview_summary": "string"
}}
"""
        return self._generate_json(prompt, FinalReport)

    def _generate_json(self, prompt: str, schema: type[T]) -> T:
        data = self._generate_raw_json(prompt)
        try:
            return schema.model_validate(data)
        except ValidationError as exc:
            raise AIResponseError(f"Gemini JSON failed schema validation: {exc}") from exc

    def _generate_raw_json(self, prompt: str) -> dict[str, Any]:
        response = self.model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.65,
                "response_mime_type": "application/json",
            },
        )
        text = (response.text or "").strip()
        if not text:
            raise AIResponseError("Gemini returned an empty response.")

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                raise AIResponseError("Gemini response did not contain JSON.")
            return json.loads(match.group(0))
