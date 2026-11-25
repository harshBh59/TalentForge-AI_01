import random

import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from nlp.interview_qa import get_questions_for_role, evaluate_answer
from speech.speech_to_text import transcribe_audio_bytes
from speech.text_to_speech import synthesize_speech
from config import INTERVIEW_QUESTIONS

# This project has gone through a couple of theme-module iterations
# (utils/theme.py vs. a root-level theme.py with different function
# names) — try the known variants so this page matches whichever one
# is actually active, and fall back to plain Streamlit if neither matches.
_HAS_THEME = False
try:
    from theme import inject_theme as apply_custom_theme, page_header as _page_header, section_title as _section_title
    _HAS_THEME = True
    _THEME_STYLE = "root"
except ImportError:
    try:
        from utils.theme import apply_custom_theme, render_section_header as _section_title
        _HAS_THEME = True
        _THEME_STYLE = "utils"
    except ImportError:
        _THEME_STYLE = None

st.set_page_config(page_title="Voice Interview - TalentForge AI", page_icon="🗣️", layout="wide")
if _HAS_THEME:
    apply_custom_theme()
render_auth_sidebar()
require_login()

user = current_user()

if _THEME_STYLE == "root":
    _page_header("🗣️", "One-on-One Voice Interview",
                 "A spoken, back-and-forth mock interview. The AI asks each question out loud; you answer by "
                 "recording your voice. Transcription and scoring run locally — nothing leaves your machine.")
elif _THEME_STYLE == "utils":
    _section_title("One-on-One Voice Interview", "🗣️",
                    "A spoken, back-and-forth mock interview. The AI asks each question out loud; you answer by "
                    "recording your voice. Transcription and scoring run locally — nothing leaves your machine.")
else:
    st.title("🗣️ One-on-One Voice Interview")
    st.caption(
        "A spoken, back-and-forth mock interview. The AI asks each question out loud; you answer by "
        "recording your voice. Transcription and scoring run locally — nothing leaves your machine."
    )

QUESTIONS_PER_SESSION = 5


def _reset_session():
    for key in ["vi_questions", "vi_index", "vi_results", "vi_role", "vi_active", "vi_audio_cache"]:
        st.session_state.pop(key, None)


def _start_session(role: str):
    bank = get_questions_for_role(role)
    n = min(QUESTIONS_PER_SESSION, len(bank))
    st.session_state["vi_questions"] = random.sample(bank, n)
    st.session_state["vi_index"] = 0
    st.session_state["vi_results"] = []
    st.session_state["vi_role"] = role
    st.session_state["vi_active"] = True
    st.session_state["vi_audio_cache"] = {}


# ---------------- Not started yet: role picker ----------------
if not st.session_state.get("vi_active"):
    st.markdown("### Start a session")
    role = st.selectbox(
        "Interview track",
        list(INTERVIEW_QUESTIONS.keys()),
        index=list(INTERVIEW_QUESTIONS.keys()).index(user.get("target_role", "general"))
        if user.get("target_role") in INTERVIEW_QUESTIONS else 0,
        key="vi_role_select",
    )
    st.caption(f"Each session asks {QUESTIONS_PER_SESSION} questions from this track, one at a time.")
    if st.button("🎬 Start voice interview", type="primary"):
        _start_session(role)
        st.rerun()

# ---------------- Session in progress ----------------
else:
    questions = st.session_state["vi_questions"]
    idx = st.session_state["vi_index"]

    if idx < len(questions):
        current_q = questions[idx]
        results = st.session_state["vi_results"]
        already_answered = len(results) > idx

        st.markdown(f"**Question {idx + 1} of {len(questions)}**")
        st.info(current_q)

        # Synthesize (and cache) the spoken version of this question so it
        # isn't regenerated on every rerun/widget interaction.
        cache = st.session_state["vi_audio_cache"]
        if idx not in cache:
            with st.spinner("Preparing question audio..."):
                try:
                    cache[idx] = synthesize_speech(current_q)
                except Exception as e:
                    cache[idx] = None
                    st.warning(f"Voice playback unavailable ({e}) — read the question above instead.")

        if cache.get(idx):
            st.audio(cache[idx], format="audio/wav")
            st.caption("🔊 Press play to hear the question, or just read it above.")

        st.markdown("---")

        if already_answered:
            # This question was already submitted — show its saved result
            # instead of a fresh recorder, so re-clicking Submit can't
            # create a duplicate database entry.
            r = results[idx]
            st.success("Answer recorded and scored.")
            st.markdown(f"**You said:** {r['transcript']}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall", f"{r['overall_score']}/100")
            c2.metric("Relevance", f"{r['relevance_score']}/100")
            c3.metric("Specificity", f"{r['specificity_score']}/100")
            st.caption(r["feedback"])

            if st.button("Next question \u2192", type="primary"):
                st.session_state["vi_index"] += 1
                st.rerun()
        else:
            st.markdown("**Your answer**")
            answer_audio = st.audio_input("Record your spoken answer", key=f"vi_answer_{idx}")

            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.button("Submit answer", type="primary", disabled=answer_audio is None)
            with col2:
                skip = st.button("Skip this question")

            if submit and answer_audio is not None:
                with st.spinner("Transcribing your answer..."):
                    transcript = transcribe_audio_bytes(answer_audio.getvalue(), suffix=".wav")

                if not transcript.strip():
                    st.warning("Couldn't hear anything in that recording — try again, a bit closer to the mic.")
                else:
                    with st.spinner("Scoring your answer..."):
                        result = evaluate_answer(current_q, transcript)

                    db.save_interview_result(
                        user["id"], f"{st.session_state['vi_role']} (voice)", current_q, transcript,
                        result["sentiment_label"], result["sentiment_score"],
                        result["relevance_score"], result["overall_score"],
                        result["specificity_score"], result["feedback"],
                    )

                    st.session_state["vi_results"].append({
                        "question": current_q,
                        "transcript": transcript,
                        **result,
                    })
                    st.rerun()

            if skip:
                st.session_state["vi_index"] += 1
                st.rerun()

    else:
        # ---------------- Session complete: summary ----------------
        st.success("Session complete! 🎉")
        results = st.session_state["vi_results"]

        if results:
            avg_score = round(sum(r["overall_score"] for r in results) / len(results), 1)
            st.metric("Session average score", f"{avg_score}/100", help=f"Based on {len(results)} questions answered")

            st.markdown("### Question-by-question breakdown")
            for i, r in enumerate(results):
                with st.expander(f"Q{i + 1}: {r['question']}"):
                    st.write(f"**You said:** {r['transcript']}")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Overall", f"{r['overall_score']}/100")
                    c2.metric("Relevance", f"{r['relevance_score']}/100")
                    c3.metric("Specificity", f"{r['specificity_score']}/100")
                    st.caption(r["feedback"])
        else:
            st.info("No questions were answered this session.")

        if st.button("🔁 Start another session", type="primary"):
            _reset_session()
            st.rerun()

st.markdown("---")
st.caption(
    "Voice interview sessions are saved to your interview history alongside text-based practice "
    "(marked with \u201c(voice)\u201d) and count toward your Dashboard readiness score."
)
