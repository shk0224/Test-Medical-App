import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_symptoms_ai(user_text: str) -> list[str]:
    prompt = f"""
Extract ONLY symptoms from the text below.
Return ONLY valid JSON in this exact format:
{{"symptoms": ["symptom1", "symptom2"]}}

Rules:
- symptoms only (no diagnosis, no meds)
- lowercase
- max 8 symptoms

Text: {user_text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract symptoms only."},
            {"role": "user", "content": prompt},
        ],
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        symptoms = data.get("symptoms", [])
        if not isinstance(symptoms, list):
            return []

        cleaned = []
        for s in symptoms:
            if isinstance(s, str) and s.strip():
                cleaned.append(s.strip().lower())
        return cleaned
    except Exception:
        return []