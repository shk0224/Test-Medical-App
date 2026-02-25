import requests

def fetch_clinical_trials_with_metadata(query: str, max_results=3, use_mock_if_empty=True):
    headers = {"User-Agent": "Mozilla/5.0"}

    # Step 1: Search ClinicalTrials.gov (get NCT IDs)
    search_url = "https://clinicaltrials.gov/api/query/study_fields"
    search_params = {
        "expr": query,
        "fields": "NCTId",
        "min_rnk": 1,
        "max_rnk": max_results,
        "fmt": "json"
    }

    try:
        search_response = requests.get(search_url, params=search_params, headers=headers, timeout=10).json()

        study_fields = search_response.get("StudyFieldsResponse", {}).get("StudyFields", [])
        nct_ids = []

        for item in study_fields:
            nct_list = item.get("NCTId", [])
            if nct_list:
                nct_ids.append(nct_list[0])

        print("Found NCT IDs:", nct_ids)

        if not nct_ids:
            raise ValueError("No NCT IDs found for this query.")

        # Step 2: Fetch trial details for each NCT ID
        trials_info = []

        for nct_id in nct_ids:
            detail_url = "https://clinicaltrials.gov/api/query/full_studies"
            detail_params = {
                "expr": nct_id,
                "min_rnk": 1,
                "max_rnk": 1,
                "fmt": "json"
            }

            detail_response = requests.get(detail_url, params=detail_params, headers=headers, timeout=10).json()

            full_studies = detail_response.get("FullStudiesResponse", {}).get("FullStudies", [])
            if not full_studies:
                continue

            study = full_studies[0].get("Study", {})
            protocol = study.get("ProtocolSection", {})

            identification = protocol.get("IdentificationModule", {})
            status_module = protocol.get("StatusModule", {})
            conditions_module = protocol.get("ConditionsModule", {})
            design_module = protocol.get("DesignModule", {})
            sponsor_module = protocol.get("SponsorCollaboratorsModule", {})

            title = identification.get("BriefTitle", "No title")
            official_title = identification.get("OfficialTitle", "")
            status = status_module.get("OverallStatus", "No status")
            start_date = status_module.get("StartDateStruct", {}).get("StartDate", "No date")
            completion_date = status_module.get("CompletionDateStruct", {}).get("CompletionDate", "No date")
            conditions = conditions_module.get("ConditionList", {}).get("Condition", [])
            phases = design_module.get("PhaseList", {}).get("Phase", [])
            sponsor = sponsor_module.get("LeadSponsor", {}).get("LeadSponsorName", "No sponsor")

            url = f"https://clinicaltrials.gov/study/{nct_id}"

            print(f"Trial: {title}\n   - NCT ID: {nct_id}\n   - Status: {status}\n   - Start: {start_date}\n   - Completion: {completion_date}\n   - URL: {url}\n")

            trials_info.append({
                "nct_id": nct_id,
                "title": title,
                "official_title": official_title,
                "status": status,
                "conditions": conditions if conditions else ["No conditions listed"],
                "phases": phases if phases else ["No phase listed"],
                "sponsor": sponsor,
                "start_date": start_date,
                "completion_date": completion_date,
                "trial_url": url
            })

        if not trials_info and use_mock_if_empty:
            print("No valid trials found, returning mock data.")
            return [{
                "nct_id": "NCT00000000",
                "title": "Simulated Clinical Trial on Fever",
                "official_title": "Simulated Trial: Treatment Approaches for Fever",
                "status": "Recruiting",
                "conditions": ["Fever"],
                "phases": ["Phase 2"],
                "sponsor": "Simulated Sponsor",
                "start_date": "March 2024",
                "completion_date": "March 2025",
                "trial_url": "https://clinicaltrials.gov/study/NCT00000000"
            }]

        return trials_info

    except Exception as e:
        print(f"Error during ClinicalTrials.gov fetch: {e}")
        if use_mock_if_empty:
            return [{
                "nct_id": "NCT00000000",
                "title": "Simulated Clinical Trial on Fever",
                "official_title": "Simulated Trial: Treatment Approaches for Fever",
                "status": "Recruiting",
                "conditions": ["Fever"],
                "phases": ["Phase 2"],
                "sponsor": "Simulated Sponsor",
                "start_date": "March 2024",
                "completion_date": "March 2025",
                "trial_url": "https://clinicaltrials.gov/study/NCT00000000"
            }]
        else:
            return [{"message": f"Error: {e}"}]