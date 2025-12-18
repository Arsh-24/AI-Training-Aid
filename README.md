# Rules-Constrained AI Training Aid with Motivational Coaching

## Live Deployment

👉 **Live app:**  
https://ai-training-aid-8b84t27ivzumzycyzwd6tv.streamlit.app/

---

## Overview

This project implements a **rules-constrained AI training aid** designed to generate **safe, explainable, and sport-agnostic weekly training plans**.  

The system combines **explicit safety rules** (such as session duration limits and conservative weekly progression) with **AI-assisted plan generation and motivational coaching**, prioritising transparency, feasibility, and responsible AI use.

The artefact was developed as part of a final-year Computer Science project and focuses on **functionality, safety, and explainability**, rather than unconstrained optimisation or long-term predictive modelling.

The application is delivered as a **web-based prototype using Streamlit**, enabling rapid development, live deployment, and practical demonstration.

---

## Key Features

- **Rules-constrained plan generation**
  - Session duration limits (20–60 minutes)
  - Conservative weekly training load progression (~+10%)
  - Non-contact, low-risk activity design
- **AI-assisted training plans**
  - Sport-agnostic (e.g. boxing, running, football, generic conditioning)
  - Level-aware (novice, intermediate, advanced)
  - Structured weekly schedules
- **Explainability by design**
  - Explicit training load calculations
  - Clear session breakdowns and safety reminders
- **Motivational coaching**
  - Weekly motivational text message
  - Optional AI-generated voice output
- **User reflection**
  - Adherence tracking (completed sessions)
  - Effort tracking using RPE (Rate of Perceived Exertion)
  - Automated reflective feedback
- **PDF export**
  - Downloadable weekly training plan
- **Embedded coaching assistant**
  - Answers questions about RPE, load, rest days, and safety
- **Privacy-aware implementation**
  - No accounts or logins
  - No personal identifiers required
  - Local session state only

---

## System Architecture

- **Frontend & UI:** Streamlit  
- **Core logic:** Python (rules engine + safety guardrails)  
- **AI integration:** External Large Language Model API  
- **State management:** Streamlit session state  
- **Data handling:** Pandas (tabular plan representation)  
- **Export:** ReportLab (PDF generation)

AI-generated content is **post-processed and constrained** using explicit rules to ensure that all plans remain within predefined safety boundaries.

---

## How Training Load Works

### Rate of Perceived Exertion (RPE)

RPE is a subjective 1–10 scale representing how hard a session felt overall:

- 1 = very easy  
- 5–6 = steady but comfortable  
- 9–10 = maximal effort  

### Unit Load

Unit load is an internal measure combining:

- Session duration  
- Session intensity  

This allows the system to:
- Compare training weeks consistently
- Apply conservative progression rules
- Provide transparent explanations to users

---

## Ethical and Safety Considerations

- The system is **not medical advice**
- No diagnosis, injury treatment, or health guarantees are provided
- Users are reminded to stop if anything feels sharp, unusual, or worrying
- Data minimisation is enforced by design
- AI outputs are constrained to reduce unsafe recommendations
- Clear boundaries are maintained between coaching support and clinical guidance

---

## Installation (Local)

```bash
git clone https://github.com/Arsh-24/AI-Training-Aid.git
pip install -r requirements.txt
streamlit run app.py
