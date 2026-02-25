from fastapi import FastAPI
from pydantic import BaseModel

from functions.symptom_extractor import extract_symptoms
from functions.pubmed_articles import fetch_pubmed_articles_with_metadata
from functions.summerize_pubmed import summarize_text
from functions.clinicaltrial import fetch_clinical_trials_with_metadata
from functions.medication_guidance import get_medication_guidance

app = FastAPI()

class SymptomInput(BaseModel):
    description: str


def make_pubmed_top(pubmed_articles: list[dict], limit: int = 2) -> list[dict]:
    top = []
    for a in pubmed_articles[:limit]:
        top.append({
            "title": a.get("title", "No title"),
            "publication_date": a.get("publication_date", "No date"),
            "url": a.get("article_url", "")
        })
    return top


def make_trials_top(trials: list[dict], limit: int = 2) -> list[dict]:
    top = []
    for t in trials[:limit]:
        phases = t.get("phases", [])
        phase_value = "No phase"
        if isinstance(phases, list) and phases:
            phase_value = phases[0]

        top.append({
            "nct_id": t.get("nct_id", ""),
            "title": t.get("title", "No title"),
            "status": t.get("status", "No status"),
            "phase": phase_value,
            "url": t.get("trial_url", "")
        })
    return top


@app.post("/medication")
def medication(data: SymptomInput):
    symptom = extract_symptoms(data.description)

    # 1) AI guidance (structured JSON)
    guidance = get_medication_guidance(symptom)

    # 2) PubMed
    pubmed_articles = fetch_pubmed_articles_with_metadata(" ".join(symptom), max_results=3)

    abstracts_text = ""
    for article in pubmed_articles:
        abstract_value = article.get("abstract", "")
        abstracts_text = abstracts_text + abstract_value + "\n\n"

    abstracts_text = abstracts_text[:2000]  # keep it shorter for user-friendly summary
    pubmed_summary = summarize_text(abstracts_text) if abstracts_text.strip() else "No abstract to summarize."
    pubmed_top = make_pubmed_top(pubmed_articles, limit=2)

    # 3) ClinicalTrials
    clinical_trials = fetch_clinical_trials_with_metadata(" ".join(symptom), max_results=3)
    clinical_trials_top = make_trials_top(clinical_trials, limit=2)

    # ✅ clean, user-friendly response
    return {
        "symptom": symptom,

        "medications": guidance.get("medications", []),
        "do_this": guidance.get("do_this", []),
        "eat_this": guidance.get("eat_this", []),
        "avoid_this": guidance.get("avoid_this", []),
        "doctor_now_if": guidance.get("doctor_now_if", []),
        "disclaimer": guidance.get("disclaimer", ""),

        "pubmed_summary": pubmed_summary,
        "pubmed_top": pubmed_top,

        "clinical_trials_top": clinical_trials_top
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)