import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from vision.emotion_detector import detect_emotion
from theme import inject_theme, page_header, section_title, empty_state

st.set_page_config(page_title="Emotion - TalentForge AI", page_icon="🙂", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header(
    "🙂", "Emotion Check",
    "Take a snapshot to check how confident and composed you look before an interview. "
    "Runs locally with FER — no image leaves your machine.",
)

img = st.camera_input("Take a photo")

if img is not None:
    with st.spinner("Analyzing facial expression..."):
        result = detect_emotion(img.getvalue())

    if result["emotion"] is None:
        st.warning("No face detected — try again with better lighting and facing the camera.")
    else:
        db.save_emotion_log(user["id"], "webcam", result["emotion"], result["confidence"])

        st.success(f"Detected emotion: **{result['emotion'].title()}** "
                   f"({result['confidence'] * 100:.0f}% confidence)")

        section_title("Full breakdown")
        for emotion, score in sorted(result["all_scores"].items(), key=lambda x: -x[1]):
            st.progress(min(score, 1.0), text=f"{emotion.title()}: {score * 100:.0f}%")

        interview_relevant = {"happy", "neutral", "surprise"}
        if result["emotion"] not in interview_relevant:
            st.info(
                "For interviews, aim for a calm, neutral-to-positive expression. "
                "Try relaxing your shoulders and taking a breath before your next take."
            )

st.markdown("---")
section_title("Recent history")

history = db.get_emotion_history(user["id"])
if history:
    for h in history[:10]:
        st.markdown(
            f"""
            <div class="tf-history-row">
                <div>
                    <div class="tf-history-main">{h['emotion'].title()}</div>
                    <div class="tf-history-sub">{h['created_at'][:19]}</div>
                </div>
                <div class="tf-history-score">{h['confidence'] * 100:.0f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    empty_state("No emotion checks yet.", "🙂")
