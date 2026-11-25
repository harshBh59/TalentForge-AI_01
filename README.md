# TalentForge AI

**AI Career Intelligence & Placement Readiness Platform** — a Streamlit app that helps
candidates prepare for job placement and gives recruiters AI-ranked candidate matching,
with every AI feature running on **local, open-source models**. No external AI API calls,
no per-request cost, no data leaving your machine.

## What it does

**For candidates**
- **Resume Analyzer** — upload a PDF/DOCX/TXT resume and get an instant, explainable
  score with a full breakdown (skills, contact info, length, structure, quantified impact)
- **Resume Builder** — build a resume from a structured form and export it as `.docx`,
  scored against the same rubric as the analyzer
- **Interview Practice** — role-specific mock questions, scored on semantic relevance,
  answer specificity, and tone, with varied AI-generated coaching feedback
- **Emotion Check** — a webcam snapshot analyzed locally for facial expression/confidence
- **Voice & Delivery** — audio transcribed locally (Whisper), scored on pace and filler-word usage
- **Coding Practice** — a sandboxed runner with test cases for quick problem-solving practice
- **Dashboard** — an aggregated placement-readiness view across all of the above

**For recruiters**
- **Recruiter Console** — post a role, get every candidate's resume semantically ranked
  against it (not just keyword search)
- **Analytics** — a hiring-funnel view: applicant volume, match-score distribution, top candidates

**Platform**
- A single, dedicated **Login / Register** page (`pages/0_Login.py`) — no duplicated auth
  forms anywhere else; every other page just links to it if you're signed out
- Role-based access (`candidate` vs `recruiter`/`admin`)
- A consistent, hand-built dark theme (`theme.py`) applied across every page

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python -m spacy download en_core_web_sm

streamlit run app.py
```

The first time each AI feature runs, its model weights (HuggingFace, sentence-transformers,
FER, Whisper) download to a local cache. After that first download, everything runs fully
offline.

## Project structure

```
TalentForge-AI/
├── app.py                    # Entry point: theme, auth, home page with clickable feature cards
├── theme.py                  # Global dark theme + reusable UI components (cards, headers, chips)
├── config.py                 # Paths, model names, constants, interview question bank
├── database.py                # SQLite schema + all CRUD functions (single source of DB access)
├── auth.py                    # Register/login/logout, session helpers, role gating
├── requirements.txt
│
├── pages/
│   ├── 0_Login.py               # The one and only login/register page
│   ├── Profile.py                # Edit profile, snapshot of activity
│   ├── Resume.py                  # Upload/parse/score a resume
│   ├── ResumeBuilder.py            # Build a resume from scratch, export .docx
│   ├── Interview.py                 # Mock interview Q&A with relevance/specificity/tone scoring
│   ├── VoiceInterview.py             # One-on-one SPOKEN mock interview (AI asks aloud, you answer aloud)
│   ├── Emotion.py                    # Webcam facial emotion check
│   ├── Voice.py                       # Audio upload → transcript + delivery analysis
│   ├── Recruter.py                     # Post jobs, view/rank candidates
│   ├── Dashboard.py                     # Candidate progress charts
│   ├── Analytics.py                      # Recruiter hiring-funnel analytics
│   └── coding.py                          # Sandboxed coding practice problems
│
├── nlp/
│   ├── resume_parser.py         # spaCy-based contact/skill/section extraction
│   └── interview_qa.py           # Semantic relevance + specificity + tone scoring, coach feedback
│
├── ml/
│   ├── resume_scorer.py          # Rule-based, explainable resume scoring + sub-score breakdown
│   └── job_matcher.py             # sentence-transformers resume↔job semantic matching
│
├── vision/
│   └── emotion_detector.py        # FER-based facial emotion detection
│
├── speech/
│   ├── speech_to_text.py           # Local Whisper transcription
│   ├── text_to_speech.py            # Local pyttsx3 TTS (AI speaks interview questions aloud)
│   └── voice_analysis.py            # Pace / filler-word analysis
│
└── utils/
    ├── helpers.py                   # PDF/DOCX/TXT text extraction
    ├── resume_doc_builder.py         # Generates .docx resumes from Resume Builder form data
    └── validators.py                  # Email/username/password validation
```

## How scoring works (the honest version)

- **Resume scoring** is rule-based and fully explainable — it checks skill coverage, contact
  completeness, length, section structure, and quantified-impact language (action verbs +
  numbers). No black-box model; every point is traceable to something in the resume.
- **Interview scoring** blends three local signals: semantic similarity between question and
  answer (sentence-transformers), a specificity heuristic (numbers, outcome language,
  structure), and a sentiment/tone pipeline. Feedback text is randomly varied from a bank of
  coach-style responses so repeated practice doesn't feel robotic.
- **Job matching** is pure semantic similarity (sentence-transformers embeddings) between a
  resume and a job description — no keyword matching involved.

None of these are fine-tuned models; they're pretrained open-source models combined with
hand-written scoring logic. That's a deliberate, explainable design choice, not a limitation
to apologize for.

## Known limitations

- Interview relevance/specificity scoring is a heuristic blend, not a fine-tuned model
- Coding sandbox runs in a subprocess with a timeout but no OS-level isolation (seccomp/
  containers) — fine for personal practice, not for hosting untrusted code publicly
- Recruiter re-matching re-inserts an `applications` row on every run, which can create
  duplicates over repeated runs — an upsert (`ON CONFLICT`) would make it idempotent
- No email verification or password-reset flow yet

## Roadmap

- Idempotent recruiter re-matching (upsert instead of insert)
- PDF export alongside the `.docx` Resume Builder output
- Password reset + email verification
- Auto-suggested skill gaps between a resume and a target role
- Combined real-time interview mode (webcam + voice + answer content scored together)
