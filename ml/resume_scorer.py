"""
Resume scoring — a transparent, rule-based score (0-100) derived from
the parsed resume, plus human-readable, varied feedback. Deliberately
explainable rather than a black-box model, but tuned to reward the same
signals real recruiters look for: skill coverage, contact completeness,
appropriate length, clear structure, and quantified impact language.
"""

from __future__ import annotations

import random
import re

IDEAL_WORD_COUNT_RANGE = (350, 900)
IDEAL_SECTION_COUNT = 4  # e.g. summary, experience, education, skills

IMPACT_VERBS = {
    "achieved", "improved", "increased", "reduced", "saved", "led", "launched",
    "built", "designed", "delivered", "grew", "cut", "boosted", "streamlined",
    "automated", "optimized", "scaled", "spearheaded", "mentored", "negotiated",
}
NUMBER_RE = re.compile(r"\b\d+(\.\d+)?%?\+?\b")


def _skills_feedback(skill_count: int) -> str:
    if skill_count < 5:
        return (f"Only {skill_count} recognized skills found — list more of the specific "
                 "tools, languages, and methods you've actually used.")
    elif skill_count < 10:
        return f"Decent skill coverage ({skill_count} detected) — a few more targeted keywords would help."
    return f"Strong skill coverage: {skill_count} relevant skills detected."


def _length_feedback(word_count: int, low: int, high: int) -> str:
    if word_count < low:
        return "Resume looks thin — most sections would benefit from another sentence or two of concrete detail."
    elif word_count > high:
        return "Resume runs long — tighten it to the most relevant, recent points so nothing gets skimmed past."
    return random.choice([
        "Length is in a solid range for a recruiter's first scan.",
        "Good length — enough detail without overloading the reader.",
    ])


def _structure_feedback(section_count: int, ideal: int) -> str:
    if section_count < ideal:
        return ("Add clear section headers (Summary, Experience, Education, Skills) — "
                "this also helps automated ATS parsers read it correctly.")
    return "Clear section structure makes this easy to scan quickly."


def _impact_feedback(impact_hits: int, number_hits: int) -> str:
    if impact_hits == 0 and number_hits == 0:
        return ("Bullet points read as duties rather than results — try rewriting a few to start with "
                "an action verb and end with a measurable outcome (e.g. 'reduced load time by 30%').")
    elif impact_hits < 3 or number_hits < 2:
        return "Some quantified impact shows through — add a metric to a couple more bullet points to strengthen it."
    return "Good use of action verbs and metrics — this reads like measurable, evidence-backed impact."


def score_resume(parsed: dict) -> tuple[float, str]:
    feedback_lines = []
    score = 0.0

    full_text = " ".join(parsed.get("sections", {}).values()).lower()

    # --- Skills coverage (30 points) ---
    skill_count = len(parsed.get("skills", []))
    skill_points = min(skill_count / 8, 1.0) * 30
    score += skill_points
    feedback_lines.append(_skills_feedback(skill_count))

    # --- Contact completeness (10 points) ---
    contact_points = 0
    if parsed.get("email"):
        contact_points += 5
    else:
        feedback_lines.append("No email address detected — make sure it's clearly listed near the top.")
    if parsed.get("phone"):
        contact_points += 5
    else:
        feedback_lines.append("No phone number detected.")
    score += contact_points

    # --- Length / depth (20 points) ---
    word_count = parsed.get("word_count", 0)
    low, high = IDEAL_WORD_COUNT_RANGE
    if word_count < low:
        length_points = (word_count / low) * 20
    elif word_count > high:
        overflow_ratio = min((word_count - high) / high, 1.0)
        length_points = 20 * (1 - 0.5 * overflow_ratio)
    else:
        length_points = 20
    score += length_points
    feedback_lines.append(_length_feedback(word_count, low, high))

    # --- Structure / sections (20 points) ---
    sections = parsed.get("sections", {})
    section_points = min(len(sections) / IDEAL_SECTION_COUNT, 1.0) * 20
    score += section_points
    feedback_lines.append(_structure_feedback(len(sections), IDEAL_SECTION_COUNT))

    # --- Quantified impact (20 points) — the signal that most separates a
    # forgettable resume from a strong one: action verbs + numbers. ---
    impact_hits = sum(1 for verb in IMPACT_VERBS if verb in full_text)
    number_hits = len(NUMBER_RE.findall(full_text))
    impact_points = min(impact_hits / 5, 1.0) * 12 + min(number_hits / 4, 1.0) * 8
    score += impact_points
    feedback_lines.append(_impact_feedback(impact_hits, number_hits))

    score = round(min(score, 100.0), 1)
    feedback = " ".join(feedback_lines)
    return score, feedback


def score_breakdown(parsed: dict) -> dict:
    """Returns the same signals as sub-scores (0-100 each) for a richer UI
    (e.g. a radar/bar chart) rather than just one blended number.
    """
    full_text = " ".join(parsed.get("sections", {}).values()).lower()

    skill_count = len(parsed.get("skills", []))
    skills_pct = round(min(skill_count / 8, 1.0) * 100, 1)

    contact_pct = round(
        (50 if parsed.get("email") else 0) + (50 if parsed.get("phone") else 0), 1
    )

    word_count = parsed.get("word_count", 0)
    low, high = IDEAL_WORD_COUNT_RANGE
    if word_count < low:
        length_pct = round((word_count / low) * 100, 1)
    elif word_count > high:
        overflow_ratio = min((word_count - high) / high, 1.0)
        length_pct = round(100 * (1 - 0.5 * overflow_ratio), 1)
    else:
        length_pct = 100.0

    structure_pct = round(min(len(parsed.get("sections", {})) / IDEAL_SECTION_COUNT, 1.0) * 100, 1)

    impact_hits = sum(1 for verb in IMPACT_VERBS if verb in full_text)
    number_hits = len(NUMBER_RE.findall(full_text))
    impact_pct = round(min(impact_hits / 5, 1.0) * 60 + min(number_hits / 4, 1.0) * 40, 1)

    return {
        "Skills": skills_pct,
        "Contact info": contact_pct,
        "Length": length_pct,
        "Structure": structure_pct,
        "Impact language": impact_pct,
    }


def missing_skills_for_role(current_skills: list[str], target_keywords: list[str]) -> list[str]:
    current = {s.lower() for s in current_skills}
    return [k for k in target_keywords if k.lower() not in current]
