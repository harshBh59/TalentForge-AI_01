"""
Central configuration for TalentForge AI.
Keep all paths, model names, and tunables here so every module
imports from a single source of truth.
"""

import os

# ---------- Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "talentforge.db")
SAVED_MODELS_DIR = os.path.join(BASE_DIR, "saved_models")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# ---------- Local model names (all open-source / HuggingFace / spaCy) ----------
SPACY_MODEL = "en_core_web_sm"
SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
EMOTION_TEXT_MODEL = "j-hartmann/emotion-english-distilroberta-base"
SENTENCE_EMBED_MODEL = "all-MiniLM-L6-v2"
ASR_MODEL = "openai/whisper-base"

# ---------- App constants ----------
APP_NAME = "TalentForge AI"
ROLES = ["candidate", "recruiter", "admin"]

SKILL_KEYWORDS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "nosql",
    "react", "angular", "vue", "node.js", "django", "flask", "fastapi",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn",
    "git", "linux", "rest api", "graphql", "microservices",
    "agile", "scrum", "communication", "leadership", "project management",
    "excel", "power bi", "tableau", "data analysis", "data engineering",
]

# ---------- Interview question bank ----------
INTERVIEW_QUESTIONS = {
    "software engineer": [
        "Tell me about a challenging bug you fixed recently.",
        "How do you approach designing a scalable system?",
        "Explain the difference between REST and GraphQL.",
        "Describe a time you disagreed with a teammate's technical decision.",
        "How do you keep your skills up to date?",
    ],
    "data analyst": [
        "Walk me through how you'd clean a messy dataset.",
        "How do you decide which chart to use for a given dataset?",
        "Tell me about a time your analysis changed a business decision.",
        "What's the difference between correlation and causation?",
        "How do you handle stakeholders who misinterpret data?",
    ],
    "product manager": [
        "How do you prioritize a product backlog?",
        "Tell me about a product launch that didn't go as planned.",
        "How do you gather and weigh user feedback?",
        "Describe how you'd measure the success of a new feature.",
        "How do you handle conflicting priorities from stakeholders?",
    ],
    "general": [
        "Tell me about yourself.",
        "What's your greatest professional strength?",
        "Describe a time you failed and what you learned.",
        "Why do you want this role?",
        "Where do you see yourself in five years?",
    ],
}
