"""
Speech-to-text using a local Whisper model through HuggingFace transformers.
No external API calls — model runs on-device (CPU or GPU if available).

Audio is decoded in Python (soundfile / librosa) and passed to the model as a
16 kHz float array, so the external `ffmpeg` program is NOT required for WAV
recordings (the browser microphone input) or for formats libsndfile can read
(WAV, FLAC, OGG, MP3). Only formats such as M4A still need ffmpeg.
"""

from __future__ import annotations

import functools
import io
import os
import tempfile

import numpy as np
import soundfile as sf
from transformers import pipeline

from config import ASR_MODEL

TARGET_SR = 16000


@functools.lru_cache(maxsize=1)
def _load_asr_pipeline():
    return pipeline("automatic-speech-recognition", model=ASR_MODEL)


def _decode_audio(audio_bytes: bytes, suffix: str = ".wav") -> np.ndarray:
    """Returns mono float32 audio at 16 kHz, decoded without ffmpeg when possible."""
    data, sr = None, None
    try:
        data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=False)
    except Exception:
        pass

    if data is None:
        # Formats libsndfile cannot read (e.g. .m4a): librosa may fall back to
        # ffmpeg/audioread, which must then be installed on the machine.
        import librosa
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            data, sr = librosa.load(tmp_path, sr=None, mono=True)
        except Exception as exc:
            raise RuntimeError(
                "Could not decode this audio file. Please record in the app or upload "
                "a WAV/MP3/OGG/FLAC file, or install ffmpeg to use other formats."
            ) from exc
        finally:
            os.remove(tmp_path)

    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != TARGET_SR:
        import librosa
        data = librosa.resample(data, orig_sr=sr, target_sr=TARGET_SR)
    return np.ascontiguousarray(data, dtype=np.float32)


def transcribe_audio_bytes(audio_bytes: bytes, suffix: str = ".wav") -> str:
    """Decodes the audio in memory and returns the transcript text."""
    asr = _load_asr_pipeline()
    audio = _decode_audio(audio_bytes, suffix)
    kwargs = {}
    if len(audio) > 30 * TARGET_SR:          # Whisper handles 30 s windows; chunk longer audio
        kwargs["chunk_length_s"] = 30
    result = asr({"raw": audio, "sampling_rate": TARGET_SR}, **kwargs)
    return result["text"].strip()