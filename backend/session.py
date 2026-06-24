import json
from typing import List, Dict, Optional

class InterviewSession:
    """Manages interview state and progression"""
    
    def __init__(self, session_id):
        self.session_id = session_id
        self.questions = self._load_questions()
        self.current_index = 0
        self.follow_up_count = 0
        self.current_conversation = []
        self.completed_questions = []
        self.finished = False
    
    def _load_questions(self) -> List[Dict]:
        """Load questions from dataset"""
        try:
            with open("dataset/qa_dataset.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback questions if dataset missing
            return [
                {
                    "id": 1,
                    "domain": "HR",
                    "question": "Tell me about yourself.",
                    "ideal_answer": "I'm a software engineer with experience in...",
                    "key_points": ["experience", "skills", "goals"]
                }
            ]
    
    def get_current_question(self) -> Optional[Dict]:
        """Get current question or None if finished"""
        if self.current_index < len(self.questions):
            return self.questions[self.current_index]
        self.finished = True
        return None
    
    def next_question(self):
        """Move to next question"""
        self.current_index += 1
        if self.current_index >= len(self.questions):
            self.finished = True
    
    def add_conversation(self, candidate_answer: str, interviewer_response: str):
        """Add a conversation turn"""
        turn = {
            "candidate": candidate_answer,
            "interviewer": interviewer_response,
            "question": self.get_current_question()["question"] if self.get_current_question() else ""
        }
        self.current_conversation.append(turn)
    
    def complete_question(self, evaluation: Dict):
        """Mark current question as completed with scores"""
        current_q = self.get_current_question()
        if current_q:
            self.completed_questions.append({
                "question": current_q["question"],
                "domain": current_q["domain"],
                "candidate_answer": self.current_conversation[-1]["candidate"] if self.current_conversation else "",
                "scores": {
                    "technical": evaluation.get("technical_score", 5),
                    "communication": evaluation.get("communication_score", 5),
                    "confidence": evaluation.get("confidence_score", 5),
                    "overall": evaluation.get("overall_score", 5)
                },
                "feedback": evaluation.get("feedback", ""),
                "overall_score": evaluation.get("overall_score", 5)
            })
    
    def reset(self):
        """Reset session"""
        self.current_index = 0
        self.follow_up_count = 0
        self.current_conversation = []
        self.completed_questions = []
        self.finished = False
    
    def get_history(self) -> List[Dict]:
        """Get complete conversation history with scores"""
        history = []
        for i, q in enumerate(self.completed_questions):
            history.append({
                "question": q["question"],
                "domain": q["domain"],
                "answer": q["candidate_answer"],
                "overall_score": q["overall_score"],
                "feedback": q["feedback"]
            })
        
        # If we have current conversation but not completed yet
        if not self.finished and self.current_conversation:
            current_q = self.get_current_question()
            if current_q and self.current_conversation:
                last_turn = self.current_conversation[-1]
                history.append({
                    "question": current_q["question"],
                    "domain": current_q["domain"],
                    "answer": last_turn["candidate"],
                    "overall_score": 5,  # Default score
                    "feedback": "Answer pending evaluation"
                })
        
        return history