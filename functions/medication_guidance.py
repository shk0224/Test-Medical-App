import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_medication_guidance(symptoms: list[str]) -> dict:
    symptom_text = ", ".join(symptoms) if symptoms else "unknown"

    prompt = f"""
You are a general health information assistant. Not medical advice.

Symptoms: {symptom_text}

Return ONLY a valid JSON object with EXACTLY these keys:
- "medications": array of OTC medication NAMES only (no dosage, no prescription drugs)
- "do_this": array of practical home-care steps
- "eat_this": array of foods/drinks that may help (hydration-focused)
- "avoid_this": array of things to avoid
- "doctor_now_if": array of red-flag symptoms when urgent care is needed
- "disclaimer": string (one short safety disclaimer)

Rules:
- Keep each list item short (1 line).
- No extra keys.
- No markdown. Only pure JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You provide general health information, not medical advice."},
            {"role": "user", "content": prompt}
        ],
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        return data
    except Exception:
        return {
            "medications": [],
            "do_this": [],
            "eat_this": [],
            "avoid_this": [],
            "doctor_now_if": [],
            "disclaimer": "General info only. Consult a clinician for medical advice."
        }