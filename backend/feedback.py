import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

def generate_feedback(history):
    """Generate comprehensive interview feedback"""
    
    if not history:
        return {
            "overall_score": 0,
            "strengths": [],
            "improvements": [],
            "summary": "No interview data available."
        }
    
    # Calculate average score
    total_score = sum(item.get("overall_score", 0) for item in history)
    average_score = round(total_score / len(history), 1)
    
    # Prepare interview data
    interview_data = ""
    for item in history:
        interview_data += f"""
Question: {item['question']}
Domain: {item['domain']}
Score: {item['overall_score']}
Feedback: {item['feedback']}
Answer: {item['answer'][:200]}...
---
"""
    
    prompt = f"""
You are an expert interview coach providing final feedback.

**Interview Data:**
{interview_data}

**Average Score:** {average_score}

**Your Task:**
Generate detailed, constructive feedback for the candidate.

**Format Requirements:**
Return ONLY valid JSON with the following structure:

{{
    "overall_score": {average_score},
    "strengths": [
        "Specific strength 1",
        "Specific strength 2",
        "Specific strength 3"
    ],
    "improvements": [
        "Specific area for improvement 1",
        "Specific area for improvement 2",
        "Specific area for improvement 3"
    ],
    "summary": "A 2-3 sentence summary of overall performance"
}}

**Guidelines:**
- Strengths should be specific and actionable
- Improvements should be constructive and encouraging
- Summary should be professional and balanced
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 300
            }
        )
        
        text = response.text.strip()
        if "```" in text:
            text = text.replace("```json", "").replace("```", "").strip()
        
        result = json.loads(text)
        
        # Ensure all fields exist
        result["strengths"] = result.get("strengths", ["Good communication"])
        result["improvements"] = result.get("improvements", ["Consider more detailed examples"])
        result["summary"] = result.get("summary", "Interview completed successfully.")
        
        return result
    
    except Exception as e:
        print(f"Feedback error: {e}")
        
        # Generate fallback feedback
        strengths = []
        improvements = []
        
        for item in history:
            score = item.get("overall_score", 0)
            if score >= 7:
                strengths.append(item.get("domain", "General"))
            else:
                improvements.append(item.get("domain", "General"))
        
        return {
            "overall_score": average_score,
            "strengths": list(set(strengths)) or ["Communication"],
            "improvements": list(set(improvements)) or ["More technical depth"],
            "summary": f"Overall performance was {average_score}/10. Keep practicing!"
        }