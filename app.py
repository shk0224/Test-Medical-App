from fastapi import FastAPI
from pydantic import BaseModel

from functions.symptom_extractor import extract_symptoms
from functions.diagnosis_symptoms import get_diagnosis
from functions.pubmed_articles import fetch_pubmed_articles_with_metadata
from functions.summerize_pubmed import summarize_text
from functions.clinicaltrial import fetch_clinical_trials_with_metadata

app = FastAPI()

class SymptomInput(BaseModel):
    description: str

@app.post("/medication")
def medication(data: SymptomInput):
    symptom = extract_symptoms(data.description)

    # This function will now be used to generate medication names (OTC suggestion prompt should be inside get_diagnosis)
    medication_result = get_diagnosis(symptom)

    pubmed_articles = fetch_pubmed_articles_with_metadata(" ".join(symptom))

    abstracts_text = ""
    for article in pubmed_articles:
        abstract_value = article.get("abstract", "")
        abstracts_text = abstracts_text + abstract_value + "\n\n"

    abstracts_text = abstracts_text[:3000]
    pubmed_summary = summarize_text(abstracts_text) if abstracts_text.strip() else "No abstract to summarize."

    clinical_trials = fetch_clinical_trials_with_metadata(" ".join(symptom))

    return {
        "symptom": symptom,
        "medication": medication_result,
        "pubmed_articles": pubmed_articles,
        "pubmed_summary": pubmed_summary,
        "clinical_trials": clinical_trials
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)