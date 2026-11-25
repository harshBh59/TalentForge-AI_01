import pandas as pd
import plotly.express as px
import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from theme import inject_theme, page_header, section_title

st.set_page_config(page_title="Dashboard - TalentForge AI", page_icon="📊", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header("📊", "My Dashboard", "Your placement readiness, tracked over time.")

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E4E2FF"),
    colorway=["#7C5CFF", "#22D3EE", "#FF7AD9", "#5B8CFF", "#B389FF"],
    margin=dict(t=20, l=10, r=10, b=10),
)

resumes = db.get_resumes_by_user(user["id"])
interviews = db.get_interview_history(user["id"])
emotions = db.get_emotion_history(user["id"])
voice_logs = db.get_voice_history(user["id"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Latest resume score", f"{resumes[0]['score']}/100" if resumes else "—")
c2.metric("Interview sessions", len(interviews))
avg_interview = round(sum(i["overall_score"] for i in interviews) / len(interviews), 1) if interviews else 0
c3.metric("Avg. interview score", f"{avg_interview}/100" if interviews else "—")
c4.metric("Voice recordings", len(voice_logs))

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    section_title("Interview score trend")
    if interviews:
        df = pd.DataFrame(interviews)[::-1]
        df["created_at"] = pd.to_datetime(df["created_at"])
        fig = px.line(df, x="created_at", y="overall_score", markers=True,
                       labels={"created_at": "Date", "overall_score": "Score"})
        fig.update_layout(**PLOTLY_LAYOUT)
        fig.update_traces(line=dict(width=3), marker=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Practice a mock interview to see your trend here.")

with col2:
    section_title("Emotion distribution")
    if emotions:
        df = pd.DataFrame(emotions)
        counts = df["emotion"].value_counts().reset_index()
        counts.columns = ["emotion", "count"]
        fig = px.pie(counts, names="emotion", values="count", hole=0.45)
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Run an emotion check to see your distribution here.")

st.markdown("---")
section_title("Resume score history")
if resumes:
    df = pd.DataFrame(resumes)[::-1]
    df["uploaded_at"] = pd.to_datetime(df["uploaded_at"])
    fig = px.bar(df, x="uploaded_at", y="score", labels={"uploaded_at": "Upload date", "score": "Score"})
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.caption("Upload a resume to see your score history here.")

st.markdown("---")
section_title("Readiness summary")

readiness_bits = []
if resumes:
    readiness_bits.append(("Resume", resumes[0]["score"]))
if interviews:
    readiness_bits.append(("Interview", avg_interview))
if voice_logs:
    avg_fillers = sum(v["filler_word_count"] for v in voice_logs) / len(voice_logs)
    voice_score = max(0, 100 - avg_fillers * 5)
    readiness_bits.append(("Delivery", round(voice_score, 1)))

if readiness_bits:
    overall_readiness = round(sum(v for _, v in readiness_bits) / len(readiness_bits), 1)
    st.metric("Overall placement readiness", f"{overall_readiness}/100")
    for label, val in readiness_bits:
        st.progress(min(val / 100, 1.0), text=f"{label}: {val}/100")
else:
    st.caption("Use Resume, Interview, and Voice tools to build your readiness profile.")
