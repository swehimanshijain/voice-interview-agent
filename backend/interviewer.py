import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def evaluate_answer(
    question,
    ideal_answer,
    key_points,
    conversation_history,
    latest_answer,
    follow_up_count
):

    history = ""

    for turn in conversation_history:

        history += f"""
Candidate: {turn['candidate']}
Interviewer: {turn['interviewer']}
"""

    prompt = f"""

You are an experienced Software Engineering Interviewer.

You are conducting a REAL interview.

You are NOT an examiner.
You are NOT a teacher.

You should behave exactly like a professional interviewer who:

- evaluates answers
- guides candidates when needed
- asks natural follow-up questions
- helps candidates improve
- stays conversational

------------------------------------

CURRENT QUESTION

{question}

------------------------------------

IDEAL ANSWER
(For evaluation only. Never reveal directly.)

{ideal_answer}

------------------------------------

KEY POINTS
(For evaluation only. Never reveal directly.)

{key_points}

------------------------------------

PREVIOUS CONVERSATION

{history}

------------------------------------

LATEST ANSWER

{latest_answer}

------------------------------------

FOLLOW UP COUNT

{follow_up_count}

------------------------------------

EVALUATION RULES

1. Compare candidate answer against ideal answer.

2. Score honestly.

3. If answer is strong:

- praise briefly
- move to next question

4. If answer is partially correct:

- explain what is missing
- give a small hint
- ask a follow-up question

Example:

Candidate:
"Process and thread are almost same."

Good interviewer:

"You're moving in the right direction, but think about how memory is managed in each case. Can you explain whether processes and threads use separate memory spaces?"

5. If answer is completely wrong:

- politely explain that some important concepts are missing
- guide candidate toward the correct direction
- ask one follow-up question

Example:

"That's a reasonable attempt. Consider how operating systems allocate resources and memory. Can you think about how processes and threads differ in that regard?"

6. NEVER reveal:

- ideal answer
- complete solution
- complete explanation

7. Give hints only.

8. Maximum follow-ups = 2

If follow_up_count >= 2

set:

move_next = true

follow_up = ""

9. If answer is completely unrelated:

technical score should be low

10. Feedback should be written for final evaluation.

------------------------------------

RETURN JSON ONLY

{{
"technical_score":0,
"communication_score":0,
"confidence_score":0,
"overall_score":0,
"feedback":"string",
"follow_up":"string",
"move_next":false
}}

------------------------------------

SCORING

technical_score:
0-10

communication_score:
0-10

confidence_score:
0-10

overall_score:
average

------------------------------------

FEEDBACK FORMAT

Mention:

- what was good
- what was missing
- one improvement suggestion

Keep it 2-3 sentences.

------------------------------------

JSON ONLY
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")
        text = text.replace("```", "")

    try:

        result = json.loads(text)

        required_fields = [
            "technical_score",
            "communication_score",
            "confidence_score",
            "overall_score",
            "feedback",
            "follow_up",
            "move_next"
        ]

        for field in required_fields:

            if field not in result:
                raise Exception("Missing field")

        return result

    except Exception:

        return {
            "technical_score": 5,
            "communication_score": 5,
            "confidence_score": 5,
            "overall_score": 5,
            "feedback":
                "Your answer addressed some parts of the question, but additional detail would strengthen your response.",
            "follow_up":
                "Could you explain your answer in a little more detail?",
            "move_next": False
        }