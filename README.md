# SG Immigration Strategist

An AI agent that assesses Singapore Permanent Residence readiness using official ICA guidance and real community case patterns.

## Product Focus

This project is now intentionally centered on one job:
- evaluate how ready an applicant looks for a Singapore PR application
- separate official ICA guidance from anecdotal community signals
- return a practical readiness snapshot with risks, strengths, documents, and next steps

It does not try to predict guaranteed approval, and it does not position community anecdotes as policy.

## Problem

Singapore PR decisions can feel opaque. Applicants can usually find:
- official ICA process information and application guidance
- scattered Reddit and forum discussions about real cases

What they usually cannot find is a clean way to combine both without blurring the line between policy and anecdote.

## Solution

SG Immigration Strategist collects an applicant profile, retrieves:
- official PR guidance from ICA-related sources
- community-reported applicant case patterns

Then it generates a structured PR readiness assessment that keeps those two evidence streams visibly separate.

## Core Output

The backend returns a dashboard-ready JSON object with:
- `readiness_score`
- `eligibility_signal`
- `scoring_breakdown`
- `official_takeaways`
- `community_takeaways`
- `top_strengths`
- `top_risks`
- `missing_documents`
- `recommended_actions`
- `confidence_notes`
- `data_sources_used`
- `error_note`

## Architecture

### Scoring Principles
- The system does not use race, religion, or ethnicity as scoring variables.
- Readiness is estimated from profile stability, documentation readiness, and official-source-aligned signals.
- Community case patterns may inform qualitative risk notes, but they are not treated as hidden rules or deterministic scoring logic.

### Frontend
- React single-page experience
- Applicant intake form
- Live agent progress panel
- PR readiness dashboard

### Backend
- FastAPI API
- TinyFish retrieval for official and community source context
- OpenAI analysis step with a strict JSON response contract
- Stable fallback response if retrieval or model calls fail

## How It Works

1. The user submits a PR applicant profile.
2. The backend retrieves official ICA guidance and community discussion context.
3. The LLM evaluates readiness while keeping official and anecdotal evidence separate.
4. The frontend renders a strategy snapshot the user can act on.

## API

### `GET /health`

```json
{
  "status": "ok",
  "service": "sg-immigration-strategist"
}
```

### `POST /analyze`

Request body:

```json
{
  "age": 30,
  "nationality": "Malaysian",
  "years_in_singapore": 5,
  "pass_type": "Employment Pass",
  "profession": "Software Engineer",
  "monthly_salary": 7000,
  "education": "Bachelor's Degree",
  "marital_status": "Single",
  "spouse_status": null,
  "children_count": 0,
  "family_ties_in_singapore": false,
  "prior_rejections": 0,
  "language_ability": "English",
  "notes": "Stable employment history in Singapore",
  "official_urls": [],
  "community_urls": []
}
```

Response body:

```json
{
  "readiness_score": 78,
  "eligibility_signal": "moderate",
  "scoring_breakdown": {
    "rubric_name": "singapore_pr_readiness_v1",
    "preliminary_score": 76,
    "final_score": 78,
    "score_adjustment": {
      "direction": "up",
      "delta": 2,
      "driver": "official_evidence",
      "reason": "Official-source evidence modestly strengthened the rubric baseline."
    },
    "source_quality": {
      "official": {
        "level": "strong",
        "label": "Official Support",
        "reason": "Official documentation expectations were well supported by retrieved ICA guidance."
      },
      "community": {
        "level": "mixed",
        "label": "Community Signals",
        "reason": "Some community case patterns were available, but coverage was uneven."
      }
    },
    "band_guidance": {
      "low": "0-49: early, weak, or highly incomplete PR profile",
      "moderate": "50-74: plausible PR profile with meaningful gaps or uncertainty",
      "strong": "75-100: well-developed PR profile with multiple positive signals"
    },
    "dimensions": [
      {
        "name": "residency_stability",
        "label": "Residency Stability",
        "score": 21,
        "max_score": 25,
        "reason": "Solid residency duration for a PR profile."
      },
      {
        "name": "employment_foundation",
        "label": "Employment Foundation",
        "score": 20,
        "max_score": 28,
        "reason": "Employment footing and salary profile are supportive."
      }
    ]
  },
  "official_takeaways": [
    "Official ICA guidance frames PR as a holistic assessment supported by complete documents.",
    "Employment and residency stability appear important to present clearly."
  ],
  "community_takeaways": [
    "Community cases often treat salary stability and time in Singapore as soft signals.",
    "Forum discussions remain anecdotal and do not reveal formal approval rules."
  ],
  "top_strengths": [
    "Stable employment history in Singapore",
    "Professional profile with competitive salary"
  ],
  "top_risks": [
    "Limited family ties in Singapore",
    "Holistic PR criteria remain partially opaque"
  ],
  "missing_documents": [
    "Latest payslips",
    "Employer letter",
    "Educational certificates"
  ],
  "recommended_actions": [
    "Prepare a complete employment and education evidence pack",
    "Strengthen the application narrative around long-term Singapore ties"
  ],
  "confidence_notes": [
    "Official guidance is stronger than anecdotal evidence for document expectations.",
    "Community patterns should be treated as directional only."
  ],
  "data_sources_used": {
    "official_source": "ICA PR guidance",
    "community_source": "Reddit PR discussion threads"
  },
  "error_note": null
}
```

If TinyFish fails, the API still continues without retrieval context. If OpenAI fails, the backend returns the same response shape with a fallback payload and an `error_note`.

## Local Setup

### Backend

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
python3.11 -m uvicorn app:app --reload
```

`backend/.env` should contain real local keys and must not be committed.

### Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The frontend targets `http://127.0.0.1:8000` by default.

## Secrets

- Commit `.env.example`, not real `.env` files.
- Keep real secrets only in local environment files such as `backend/.env`.
- For deployment, use platform-managed environment variable settings instead of committing secrets.
- If a real key was ever committed, remove it and rotate it immediately.

## Current Status

Hackathon prototype with the product story now aligned around:
- Singapore PR readiness
- official ICA guidance as the authoritative source
- community case patterns as anecdotal support only

## Next Improvements

- Add richer source normalization and citations
- Support multiple official ICA PR pages and better source labeling
- Improve structured explanation quality for mixed or incomplete profiles
- Add historical case clustering instead of relying on raw community threads
