# SG Immigration Strategist

An AI agent that helps assess Singapore PR/Citizenship application readiness by combining official ICA requirements with community case patterns.

## Problem
Applying for Singapore PR or citizenship can feel confusing and opaque. Applicants often struggle to understand:
- whether their profile looks competitive
- which documents they may be missing
- what factors may weaken their application
- how official requirements compare with real-world applicant experiences

## Solution
SG Immigration Strategist is a lightweight AI agent that:
1. collects an applicant profile
2. extracts official requirement information from ICA sources
3. analyzes community-reported approval/rejection patterns
4. generates a readiness assessment with risks, strengths, and next steps

## Key Features
- Applicant profile intake form
- AI-generated readiness score
- Missing document checklist
- Risk factor analysis
- Suggested next steps
- Clear separation between official information and community-derived signals

## How It Works

### 1. User Input
The user enters profile details such as:
- age
- nationality
- years in Singapore
- pass type
- profession
- salary
- education
- family status

### 2. Data Collection
The agent gathers:
- **Official data** from ICA-related sources
- **Community data** from public discussion threads and applicant case reports

### 3. AI Analysis
An LLM compares:
- the user’s submitted profile
- official application requirements
- patterns from community cases

### 4. Output
The system returns a structured assessment, including:
- readiness score
- eligibility signal
- top strengths
- top risks
- missing documents
- recommended actions
- confidence notes

## Tech Stack

### Application Stack
- **Frontend:** React
- **Backend:** FastAPI
- **AI:** OpenAI API
- **Web extraction / browsing:** TinyFish

### Development Tools
- **OpenAI ChatGPT / Codex** — used to accelerate system design, prompt engineering, debugging, and implementation during the hackathon.
- **Git & GitHub** — version control and submission
- **VS Code** — development environment
- **Node.js / npm** — frontend package management and local dev server
- **Python virtual environment** — backend dependency isolation

## Built With
- React
- FastAPI
- OpenAI
- TinyFish
- GitHub

## Demo Flow
1. User fills in applicant profile
2. App shows multi-step agent progress
3. Backend retrieves official + community source content
4. LLM generates readiness analysis
5. Dashboard displays structured results

## Example Output
```json
{
  "readiness_score": 78,
  "eligibility_signal": "moderate",
  "top_strengths": [
    "Stable employment history in Singapore",
    "Above-average salary profile"
  ],
  "top_risks": [
    "Limited years of residency",
    "No strong family ties in Singapore"
  ],
  "missing_documents": [
    "Latest payslips",
    "Employer letter",
    "Educational certificates"
  ],
  "recommended_actions": [
    "Strengthen application with longer employment history",
    "Prepare complete supporting documents"
  ],
  "confidence_notes": [
    "Official requirements are clearer than real-world approval criteria",
    "Community data is anecdotal and should not be treated as guaranteed outcome"
  ]
}
```

## Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload
```

### Backend API Contract
`GET /health`

Returns:
```json
{
  "status": "ok",
  "service": "sg-immigration-strategist"
}
```

`POST /analyze`

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
  "readiness_score": 72,
  "eligibility_signal": "moderate",
  "top_strengths": [
    "Stable work history",
    "Relevant professional background"
  ],
  "top_risks": [
    "Limited family ties in Singapore"
  ],
  "missing_documents": [
    "Payslips",
    "Employer letter"
  ],
  "recommended_actions": [
    "Prepare supporting employment documents"
  ],
  "confidence_notes": [
    "Fallback response used due to unavailable external services"
  ],
  "data_sources_used": {
    "official_source": "ICA requirements page",
    "community_source": "Public applicant discussion thread"
  },
  "error_note": null
}
```

If TinyFish fails, the API continues without retrieval context. If OpenAI fails, the API returns the same response shape with a fallback analysis and a populated `error_note`.

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend expects the backend API at `http://127.0.0.1:8000` and is currently built as a single-page flow:
- profile form
- loading progress panel
- readiness results dashboard

Optional frontend environment file:
```bash
cp .env.example .env
```

## Project Status
Hackathon prototype in progress.

## Future Improvements
- Better source validation
- More nuanced scoring model
- Document upload support
- Personalized application strategy recommendations
- Historical case comparison dashboard

## Disclaimer
This project is for informational assistance only and does not constitute legal or immigration advice.
