import re
from functions.ai_symptom_extractor import extract_symptoms_ai

def extract_symptoms(text: str) -> list[str]:
    symptoms = re.findall(r"\b(headache|fever|nausea|fatigue|pain)\b", text.lower())
    symptoms = list(set(symptoms))

    # Fallback: if regex finds nothing, use AI extraction
    if not symptoms:
        symptoms = extract_symptoms_ai(text)

    return symptoms