import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from speech.speech_to_text import transcribe_audio_bytes
from speech.voice_analysis import analyze_delivery
from theme import inject_theme, page_header, section_title, empty_state

st.set_page_config(page_title="Voice - TalentForge AI", page_icon="🎙️", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header(
    "🎙️", "Voice & Delivery Analysis",
    "Upload a short recording of yourself answering a question. "
    "Transcription runs locally with Whisper — audio never leaves your machine.",
)

audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg"])

if audio_file is not None:
    audio_bytes = audio_file.getvalue()
    suffix = "." + audio_file.name.split(".")[-1]

    st.audio(audio_bytes)

    if st.button("🎧 Analyze recording", type="primary", use_container_width=True):
        with st.spinner("Transcribing..."):
            transcript = transcribe_audio_bytes(audio_bytes, suffix)

        with st.spinner("Analyzing delivery..."):
            delivery = analyze_delivery(transcript, audio_bytes, suffix)

        db.save_voice_log(
            user["id"], transcript, delivery["duration_seconds"],
            delivery["words_per_minute"], delivery["filler_word_count"],
        )

        st.success("Analysis complete.")

        section_title("Transcript")
        st.write(transcript or "_(no speech detected)_")

        c1, c2, c3 = st.columns(3)
        c1.metric("Duration", f"{delivery['duration_seconds']}s")
        c2.metric("Pace", f"{delivery['words_per_minute']} wpm")
        c3.metric("Filler words", delivery["filler_word_count"])

        st.info(delivery["pace_feedback"])
        if delivery["filler_word_count"] > 5:
            st.warning("Lots of filler words (um, like, uh) — practice pausing silently instead.")

st.markdown("---")
section_title("Recent history")

history = db.get_voice_history(user["id"])
if history:
    for h in history[:10]:
        st.markdown(
            f"""
            <div class="tf-history-row">
                <div>
                    <div class="tf-history-main">{h['duration_seconds']}s · {h['words_per_minute']} wpm</div>
                    <div class="tf-history-sub">{h['created_at'][:19]}</div>
                </div>
                <div class="tf-history-score">{h['filler_word_count']} fillers</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    empty_state("No recordings analyzed yet.", "🎙️")
