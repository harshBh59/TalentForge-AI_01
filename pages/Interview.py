import random

import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from nlp.interview_qa import get_questions_for_role, evaluate_answer
from config import INTERVIEW_QUESTIONS
from theme import inject_theme, page_header, section_title, empty_state

st.set_page_config(page_title="Interview - TalentForge AI", page_icon="🎤", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header(
    "🎤", "Mock Interview Practice",
    "Practice real interview questions and get instant, structured feedback on relevance, "
    "specificity, and tone — every answer is scored locally, never sent to an external API.",
)

role = st.selectbox(
    "Interview track",
    list(INTERVIEW_QUESTIONS.keys()),
    index=list(INTERVIEW_QUESTIONS.keys()).index(user.get("target_role", "general"))
    if user.get("target_role") in INTERVIEW_QUESTIONS else 0,
)

if "current_question" not in st.session_state or st.session_state.get("interview_role") != role:
    st.session_state["current_question"] = random.choice(get_questions_for_role(role))
    st.session_state["interview_role"] = role

section_title("Question")
st.info(st.session_state["current_question"])

answer = st.text_area("Your answer", height=180, key="interview_answer")

col1, col2 = st.columns(2)
with col1:
    submit = st.button("Submit answer", type="primary", use_container_width=True)
with col2:
    next_q = st.button("🔀 Skip to a new question", use_container_width=True)

if next_q:
    st.session_state["current_question"] = random.choice(get_questions_for_role(role))
    st.rerun()

if submit:
    if not answer.strip():
        st.warning("Write an answer before submitting.")
    else:
        with st.spinner("Evaluating your answer..."):
            result = evaluate_answer(st.session_state["current_question"], answer)

        db.save_interview_result(
            user["id"], role, st.session_state["current_question"], answer,
            result["sentiment_label"], result["sentiment_score"],
            result["relevance_score"], result["overall_score"],
            result["specificity_score"], result["feedback"],
        )

        st.success("Answer evaluated.")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Overall score", f"{result['overall_score']}/100")
        c2.metric("Relevance", f"{result['relevance_score']}/100")
        c3.metric("Specificity", f"{result['specificity_score']}/100")
        c4.metric("Tone", result["sentiment_label"].title())

        st.markdown("**Coach feedback**")
        st.write(result["feedback"])

st.markdown("---")
section_title("Session history")

history = db.get_interview_history(user["id"])
if history:
    for h in history[:10]:
        st.markdown(
            f"""
            <div class="tf-history-row">
                <div style="max-width:75%;">
                    <div class="tf-history-main">{h['question']}</div>
                    <div class="tf-history-sub">Tone: {h['sentiment_label']} · {h['created_at'][:19]}</div>
                </div>
                <div class="tf-history-score">{h['overall_score']}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if h.get("feedback"):
            st.caption(h["feedback"])
else:
    empty_state("No interview sessions yet.", "🎤")
