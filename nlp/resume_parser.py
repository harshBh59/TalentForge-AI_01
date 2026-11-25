"""
Resume parsing built on spaCy (local, no external API calls).
Extracts contact info, name, skills, and rough section text.
"""

from __future__ import annotations

import re
import functools

import spacy

from config import SPACY_MODEL, SKILL_KEYWORDS

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d{1,3}[\s.-]?)?\(?\d{3,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}")
SECTION_HEADERS = ["experience", "education", "skills", "projects",
                    "certifications", "summary", "objective"]


@functools.lru_cache(maxsize=1)
def _load_nlp():
    """Load the spaCy model once per process. Requires:
    python -m spacy download en_core_web_sm
    """
    try:
        return spacy.load(SPACY_MODEL)
    except OSError:
        from spacy.cli import download
        download(SPACY_MODEL)
        return spacy.load(SPACY_MODEL)


def extract_contact_info(text: str) -> dict:
    email_match = EMAIL_RE.search(text)
    phone_match = PHONE_RE.search(text)
    return {
        "email": email_match.group(0) if email_match else None,
        "phone": phone_match.group(0) if phone_match else None,
    }


def extract_name(text: str) -> str | None:
    nlp = _load_nlp()
    # Only run NER on the first ~500 chars — names appear at the top of a resume.
    doc = nlp(text[:500])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = [skill for skill in SKILL_KEYWORDS if skill in lowered]
    return sorted(set(found))


def split_sections(text: str) -> dict:
    """Naive section splitter based on common resume headers."""
    lines = text.splitlines()
    sections = {}
    current = "header"
    sections[current] = []

    for line in lines:
        stripped = line.strip().lower().rstrip(":")
        matched_header = next((h for h in SECTION_HEADERS if stripped == h), None)
        if matched_header:
            current = matched_header
            sections[current] = []
        else:
            sections.setdefault(current, []).append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def parse_resume(text: str) -> dict:
    contact = extract_contact_info(text)
    return {
        "name": extract_name(text),
        "email": contact["email"],
        "phone": contact["phone"],
        "skills": extract_skills(text),
        "sections": split_sections(text),
        "word_count": len(text.split()),
    }
