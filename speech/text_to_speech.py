"""
Local text-to-speech using pyttsx3 (offline, no external API).

pyttsx3 wraps the operating system's own speech engine — SAPI5 on Windows
(built in, no extra install needed), NSSpeechSynthesizer on macOS, or
espeak on Linux (install with: sudo apt install espeak). This keeps the
"fully local, no external API" architecture consistent with the rest of
the project.
"""

from __future__ import annotations

import tempfile
import os


def synthesize_speech(text: str, rate: int = 175, volume: float = 1.0) -> bytes:
    """Converts text to spoken audio (WAV bytes) using the local OS speech
    engine via pyttsx3. Returns raw WAV bytes suitable for st.audio().
    """
    import pyttsx3  # imported lazily so pages that don't use voice mode
                     # never pay the engine-init cost

    engine = pyttsx3.init()
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as f:
            audio_bytes = f.read()
        return audio_bytes
    finally:
        engine.stop()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
