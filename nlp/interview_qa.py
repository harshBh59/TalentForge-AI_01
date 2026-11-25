"""
Interview answer evaluation.

Combines three local, no-API signals into a more realistic overall score:
1. Semantic relevance — sentence-transformers embedding similarity between
   the question and answer (catches paraphrased, on-topic answers that
   share no exact keywords).
2. Specificity — rewards concrete detail: numbers, named tools/technologies,
   and STAR-style structure (Situation/Task/Action/Result) for behavioral
   answers, which is what real interviewers actually look for.
3. Tone — a local sentiment/confidence pipeline.

Also generates varied, human-sounding qualitative feedback instead of a
single canned line, so repeated practice doesn't feel robotic.
"""

from __future__ import annotations

import functools
import random
import re

from sentence_transformers import SentenceTransformer, util
from transformers import pipeline

from config import SENTIMENT_MODEL, SENTENCE_EMBED_MODEL, INTERVIEW_QUESTIONS

STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "is",
    "are", "was", "were", "be", "with", "you", "your", "i", "me", "my",
    "how", "what", "tell", "about", "do", "did", "that", "this",
}

NUMBER_RE = re.compile(r"\b\d+(\.\d+)?%?\b")
RESULT_WORDS = {"result", "resulted", "improved", "reduced", "increased", "saved",
                "achieved", "delivered", "launched", "led", "grew", "cut", "boosted"}
FILLER_PHRASES = {"i don't know", "not sure", "no idea", "n/a"}


@functools.lru_cache(maxsize=1)
def _load_sentiment_pipeline():
    return pipeline("sentiment-analysis", model=SENTIMENT_MODEL)


@functools.lru_cache(maxsize=1)
def _load_embed_model():
    return SentenceTransformer(SENTENCE_EMBED_MODEL)


def get_questions_for_role(role: str) -> list[str]:
    role = (role or "general").lower().strip()
    return INTERVIEW_QUESTIONS.get(role, INTERVIEW_QUESTIONS["general"])


def _keywords(text: str) -> set[str]:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def semantic_relevance(question: str, answer: str) -> float:
    """0-100 semantic similarity between question and answer using local
    sentence-transformers embeddings. Catches on-topic answers that
    paraphrase rather than repeat the question's wording.
    """
    model = _load_embed_model()
    embeddings = model.encode([question, answer], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    similarity = max(0.0, min(similarity, 1.0))
    return round(similarity * 100, 1)


def specificity_score(answer: str) -> float:
    """0-100 score rewarding concrete, evidence-backed answers: numbers,
    outcome language, and enough length to actually explain something —
    the things that separate a vague answer from a strong one.
    """
    lowered = answer.lower()
    if any(phrase in lowered for phrase in FILLER_PHRASES):
        return 5.0

    word_count = len(answer.split())
    length_points = min(word_count / 90, 1.0) * 40

    number_hits = len(NUMBER_RE.findall(answer))
    number_points = min(number_hits / 2, 1.0) * 25

    result_hits = sum(1 for w in RESULT_WORDS if w in lowered)
    result_points = min(result_hits / 2, 1.0) * 20

    # Light structure bonus: multiple sentences suggest a fuller narrative
    # (situation -> action -> result) rather than a one-liner.
    sentence_count = len(re.findall(r"[.!?]+", answer))
    structure_points = min(sentence_count / 4, 1.0) * 15

    return round(min(length_points + number_points + result_points + structure_points, 100.0), 1)


def relevance_score(question: str, answer: str) -> float:
    """Blended relevance: mostly semantic similarity, with a keyword-overlap
    floor so an answer that's semantically close but keyword-empty (e.g.
    very short) doesn't get an inflated score.
    """
    q_words = _keywords(question)
    a_words = _keywords(answer)
    keyword_overlap = len(q_words & a_words) / max(len(q_words), 1) if a_words else 0.0

    semantic = semantic_relevance(question, answer)
    score = 0.8 * semantic + 0.2 * (keyword_overlap * 100)
    return round(min(score, 100.0), 1)


_FEEDBACK_OPENERS = {
    "high": [
        "Strong answer — you addressed the question directly and backed it up with specifics.",
        "This lands well. It's clear, focused, and shows real substance.",
        "Solid response — an interviewer would come away with a concrete example in mind.",
    ],
    "mid": [
        "You're on the right track, but the answer could use more concrete detail.",
        "Decent start — it answers the question, though it stays fairly general.",
        "This is workable, but right now it reads more like a summary than a story.",
    ],
    "low": [
        "This answer needs more work before it's interview-ready.",
        "Right now this doesn't give the interviewer much to go on.",
        "This feels thin — worth rebuilding with a specific example in mind.",
    ],
}

_FEEDBACK_TIPS = [
    "Try structuring it as Situation -> Task -> Action -> Result — it gives interviewers a clear story to follow.",
    "Add a number if you can (e.g. percent, hours saved, team size) — concrete metrics make claims memorable.",
    "Name the specific tool, technology, or process you used rather than describing it generically.",
    "End with the outcome — what changed because of what you did?",
    "Keep it tight: aim for 45-90 seconds of spoken answer, roughly 100-180 words.",
    "Make sure the first sentence directly answers the question before you add context.",
]


def generate_feedback(question: str, answer: str, relevance: float, specificity: float,
                       sentiment_label: str) -> str:
    """Produces a short, varied, realistic-sounding feedback paragraph instead
    of a single canned line — mirrors how a human interview coach would
    combine an overall read with one concrete, actionable tip.
    """
    combined = 0.6 * relevance + 0.4 * specificity

    if combined >= 75:
        band = "high"
    elif combined >= 50:
        band = "mid"
    else:
        band = "low"

    opener = random.choice(_FEEDBACK_OPENERS[band])
    tip = random.choice(_FEEDBACK_TIPS)

    tone_note = ""
    if sentiment_label == "NEGATIVE" and band != "low":
        tone_note = " One note: the phrasing reads a little negative or hesitant — framing it more confidently will help."

    return f"{opener} {tip}{tone_note}"


def evaluate_answer(question: str, answer: str) -> dict:
    if not answer or not answer.strip():
        return {
            "sentiment_label": "NEUTRAL",
            "sentiment_score": 0.0,
            "relevance_score": 0.0,
            "specificity_score": 0.0,
            "overall_score": 0.0,
            "feedback": "No answer was given — try writing at least a few sentences so it can be scored.",
        }

    sentiment_pipe = _load_sentiment_pipeline()
    result = sentiment_pipe(answer[:512])[0]  # truncate for model max length

    rel_score = relevance_score(question, answer)
    spec_score = specificity_score(answer)

    # Relevance matters most (did you answer the actual question), specificity
    # next (did you back it up), tone last (a confident but vague answer
    # should not outscore a specific, well-structured one).
    overall = round(0.5 * rel_score + 0.35 * spec_score + 0.15 * (result["score"] * 100), 1)

    feedback = generate_feedback(question, answer, rel_score, spec_score, result["label"])

    return {
        "sentiment_label": result["label"],
        "sentiment_score": round(result["score"], 3),
        "relevance_score": rel_score,
        "specificity_score": spec_score,
        "overall_score": overall,
        "feedback": feedback,
    }
