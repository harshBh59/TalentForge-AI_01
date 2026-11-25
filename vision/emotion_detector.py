"""
Facial emotion detection using the local FER library (MTCNN + a small CNN),
run entirely on-device — no external API calls.

Requires: pip install fer opencv-python
"""

from __future__ import annotations

import functools
import io

import cv2
import numpy as np
from PIL import Image


@functools.lru_cache(maxsize=1)
def _load_detector():
    try:
        from fer import FER          # fer <= 25.10.2
    except ImportError:
        from fer.fer import FER      # fer >= 25.10.3
    return FER(mtcnn=True)


def _to_bgr_array(image_bytes: bytes) -> np.ndarray:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def detect_emotion(image_bytes: bytes) -> dict:
    """Returns {'emotion': str, 'confidence': float, 'all_scores': dict} or
    {'emotion': None, ...} if no face was found.
    """
    detector = _load_detector()
    frame = _to_bgr_array(image_bytes)

    results = detector.detect_emotions(frame)
    if not results:
        return {"emotion": None, "confidence": 0.0, "all_scores": {}, "faces_found": 0}

    # Use the largest detected face (most likely the primary subject).
    best = max(results, key=lambda r: r["box"][2] * r["box"][3])
    scores = best["emotions"]
    top_emotion = max(scores, key=scores.get)

    return {
        "emotion": top_emotion,
        "confidence": round(scores[top_emotion], 3),
        "all_scores": {k: round(v, 3) for k, v in scores.items()},
        "faces_found": len(results),
    }
