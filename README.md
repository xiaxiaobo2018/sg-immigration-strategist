# SG Immigration Strategist

An AI agent that assesses Singapore PR readiness using official ICA guidance and real community case patterns.

## Tech Stack

![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=0b0f10)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=ffffff)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=ffffff)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=for-the-badge&logo=openai&logoColor=ffffff)
![TinyFish](https://img.shields.io/badge/TinyFish-FF8A00?style=for-the-badge&logoColor=ffffff&label=TinyFish)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=ffffff)

## What It Does

- Collects an applicant profile for Singapore PR readiness review
- Retrieves official ICA guidance and community case patterns separately
- Produces a structured readiness score, strengths, risks, missing documents, and next steps
- Keeps official guidance authoritative and community signals anecdotal

## Scoring Principles

- The system does not use race, religion, or ethnicity as scoring variables.
- Readiness is estimated from profile stability, documentation readiness, and official-source-aligned signals.
- Community case patterns may inform qualitative risk notes, but they are not treated as hidden rules or deterministic scoring logic.

## Architecture

1. The frontend collects a PR applicant profile.
2. TinyFish retrieves official and community source context.
3. The backend builds a PR-specific scoring rubric.
4. OpenAI synthesizes the evidence into a structured readiness assessment.
5. If live services fail, the app returns a stable fallback response in the same JSON shape.

## Core Output

The API returns:

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

## Quick Start

### 1. Install tools

```bash
python3.11 --version
node --version
npm --version
```

If needed:

```bash
brew install python@3.11 node
```

### 2. Start the backend

```bash
cd backend
cp .env.example .env
python3.11 -m pip install -r requirements.txt
python3.11 -m uvicorn app:app --reload
```

Put your real keys in `backend/.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TINYFISH_API_KEY=your_tinyfish_api_key_here
OPENAI_MODEL=gpt-5
TINYFISH_BASE_URL=
```

`TINYFISH_BASE_URL` is optional for the current SDK-based TinyFish flow.

### 3. Start the frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The frontend targets `http://127.0.0.1:8000` by default.

## API

### `GET /health`

```json
{
  "status": "ok",
  "service": "sg-immigration-strategist"
}
```

### `POST /analyze`

Example request:

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
  "notes": "Stable employment history in Singapore"
}
```

Example response:

```json
{
  "readiness_score": 78,
  "eligibility_signal": "moderate",
  "official_takeaways": [
    "Official ICA guidance frames PR as a holistic assessment supported by complete documents."
  ],
  "community_takeaways": [
    "Community cases often treat salary stability and time in Singapore as soft signals."
  ],
  "top_strengths": [
    "Stable employment history in Singapore"
  ],
  "top_risks": [
    "Holistic PR criteria remain partially opaque"
  ],
  "recommended_actions": [
    "Prepare a complete employment and education evidence pack"
  ],
  "error_note": null
}
```

## Secrets

- Commit `.env.example`, not real `.env` files.
- Keep real secrets only in local environment files such as `backend/.env`.
- If a real key was ever committed, rotate it immediately.

## Current State

Hackathon-ready prototype with:

- React frontend intake and readiness dashboard
- FastAPI backend scoring pipeline
- TinyFish live retrieval and browser preview
- OpenAI synthesis layer
- Stable fallback mode when live services fail
