# SG Immigration Strategist Pitch Script

## 90-Second Demo Script

Hi, we built SG Immigration Strategist, an AI agent that helps people assess how ready they are for a Singapore PR application before they submit.

The core problem is ambiguity. ICA provides official guidance on process and application requirements, but applicants still struggle to understand how competitive or complete their profile looks. At the same time, Reddit and forum discussions contain real case experiences, but those signals are anecdotal and easy to misread.

Our product combines both without mixing them up.

On the left, the user enters an applicant profile: age, nationality, years in Singapore, pass type, salary, education, family ties, and prior rejections.

When we click analyze, the backend reviews two evidence streams. First, it retrieves official ICA guidance related to Singapore PR. Second, it retrieves public community discussions that reflect real applicant case patterns.

The key design choice is separation. Official guidance stays authoritative. Community content is treated as anecdotal signal only, never as policy.

We also make the scoring boundary explicit: the system does not use race, religion, or ethnicity as scoring variables. Readiness is estimated from profile stability, documentation readiness, and signals that stay aligned with official sources.

The output is a structured PR readiness dashboard: a readiness score, an eligibility signal, official takeaways, community pattern signals, top strengths, top risks, likely missing documents, and recommended next steps.

So instead of dumping scattered information on the user, we turn it into a practical strategy snapshot they can actually act on.

We also built it to stay stable in a demo setting. If retrieval or model calls fail, the app still returns a consistent structured response instead of breaking.

SG Immigration Strategist makes Singapore PR preparation more understandable, more transparent, and more actionable.

## Shorter Backup Version

SG Immigration Strategist is an AI agent for Singapore PR readiness. It combines official ICA guidance with real community case patterns, keeps those evidence streams separate, and returns a clear dashboard with readiness score, risks, document prep signals, and next steps. The value is clarity: users get a practical PR strategy snapshot instead of raw policy pages and scattered anecdotes.
