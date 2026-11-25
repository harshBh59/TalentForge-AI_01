"""
Basic voice-delivery analysis: speaking pace and filler-word usage,
computed from a transcript plus the audio's duration.
"""

from __future__ import annotations

import re
import tempfile
import os

import librosa

FILLER_WORDS = {"um", "uh", "like", "you know", "sort of", "kind of", "basically", "actually"}


def get_audio_duration(audio_bytes: bytes, suffix: str = ".wav") -> float:
    try:  # fast path, no ffmpeg needed for WAV/FLAC/OGG/MP3
        import io
        import soundfile as sf
        return round(sf.info(io.BytesIO(audio_bytes)).duration, 2)
    except Exception:
        pass
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name
    try:
        duration = librosa.get_duration(path=tmp_path)
        return round(duration, 2)
    finally:
        os.remove(tmp_path)


def count_filler_words(transcript: str) -> int:
    lowered = f" {transcript.lower()} "
    return sum(lowered.count(f" {phrase} ") for phrase in FILLER_WORDS)


def words_per_minute(transcript: str, duration_seconds: float) -> float:
    word_count = len(re.findall(r"\w+", transcript))
    if duration_seconds <= 0:
        return 0.0
    return round(word_count / (duration_seconds / 60), 1)


def analyze_delivery(transcript: str, audio_bytes: bytes, suffix: str = ".wav") -> dict:
    duration = get_audio_duration(audio_bytes, suffix)
    wpm = words_per_minute(transcript, duration)
    fillers = count_filler_words(transcript)

    pace_feedback = "Good pace."
    if wpm < 110:
        pace_feedback = "Pace is a bit slow — aim for more energy and confidence."
    elif wpm > 170:
        pace_feedback = "Pace is quite fast — consider slowing down for clarity."

    return {
        "duration_seconds": duration,
        "words_per_minute": wpm,
        "filler_word_count": fillers,
        "pace_feedback": pace_feedback,
    }