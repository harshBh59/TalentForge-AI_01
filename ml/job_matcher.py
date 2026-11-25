"""
Semantic matching between resumes and job descriptions using a local
sentence-transformers embedding model (no external API calls).
"""

from __future__ import annotations

import functools

import numpy as np
from sentence_transformers import SentenceTransformer, util

from config import SENTENCE_EMBED_MODEL


@functools.lru_cache(maxsize=1)
def _load_model():
    return SentenceTransformer(SENTENCE_EMBED_MODEL)


def match_score(resume_text: str, job_description: str) -> float:
    """Returns a 0-100 semantic similarity score between a resume and a job posting."""
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    model = _load_model()
    embeddings = model.encode([resume_text, job_description], convert_to_tensor=True)
    similarity = util.cos_sim(embeddings[0], embeddings[1]).item()
    # cosine similarity is roughly -1..1; clamp and rescale to 0-100
    similarity = max(0.0, min(similarity, 1.0))
    return round(similarity * 100, 1)


def rank_candidates(job_description: str, candidate_texts: dict[int, str]) -> list[tuple[int, float]]:
    """candidate_texts: {user_id: resume_text}. Returns [(user_id, score), ...] sorted desc."""
    if not candidate_texts:
        return []

    model = _load_model()
    ids = list(candidate_texts.keys())
    texts = [candidate_texts[i] for i in ids]

    job_emb = model.encode(job_description, convert_to_tensor=True)
    resume_embs = model.encode(texts, convert_to_tensor=True)

    sims = util.cos_sim(job_emb, resume_embs)[0].cpu().numpy()
    sims = np.clip(sims, 0, 1) * 100

    ranked = sorted(zip(ids, sims.tolist()), key=lambda pair: pair[1], reverse=True)
    return [(uid, round(score, 1)) for uid, score in ranked]
