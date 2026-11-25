import streamlit as st

from database import create_tables
from auth import render_auth_sidebar, is_authenticated, current_user
from config import APP_NAME
from theme import inject_theme, hero, section_title, chips

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🧠",
    layout="wide",
)

inject_theme()

create_tables()
render_auth_sidebar()

hero(
    "🧠",
    "TalentForge AI",
    "AI Career Intelligence &amp; Placement Readiness Platform — parse, practice, and "
    "polish every part of your job search, powered entirely by local, open-source models.",
    badge="Career Intelligence Suite",
)

if is_authenticated():
    user = current_user()
    st.success(f"Welcome back, {user['full_name'] or user['username']}! 🚀")

    section_title("Get started")
    st.caption("Click any card below to jump straight into that tool.")

    FEATURES_COL1 = [
        ("📄", "Resume Analyzer", "Upload and score your resume against role expectations.", "pages/Resume.py"),
        ("🛠️", "Resume Builder", "Build a formatted resume from scratch and download it as .docx.", "pages/ResumeBuilder.py"),
        ("🎤", "Interview Practice", "Practice mock interview questions with instant feedback.", "pages/Interview.py"),
        ("🗣️", "Voice Interview", "A spoken, one-on-one mock interview — the AI asks, you answer aloud.", "pages/VoiceInterview.py"),
        ("🙂", "Emotion Check", "Check how confident and composed you look on camera.", "pages/Emotion.py"),
    ]
    FEATURES_COL2 = [
        ("🎙️", "Voice & Delivery", "Analyze your speaking pace and filler-word usage.", "pages/Voice.py"),
        ("💻", "Coding Practice", "Practice coding problems in a sandboxed runner.", "pages/coding.py"),
        ("📊", "Dashboard", "Track your overall placement readiness over time.", "pages/Dashboard.py"),
    ]
    FEATURES_COL3 = []
    if user["role"] in ("recruiter", "admin"):
        FEATURES_COL3.append(("🧑‍💼", "Recruiter Console", "Post jobs and review AI-ranked candidates.", "pages/Recruter.py"))
        FEATURES_COL3.append(("📈", "Analytics", "See hiring funnel metrics across your job posts.", "pages/Analytics.py"))
    FEATURES_COL3.append(("👤", "Profile", "Update your target role and personal details.", "pages/Profile.py"))

    def render_nav_card(icon: str, title: str, desc: str, page_path: str):
        with st.container(border=True):
            st.markdown(
                f"""
                <div class="tf-card-icon">{icon}</div>
                <div class="tf-card-title">{title}</div>
                <div class="tf-card-desc">{desc}</div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page_path, label="Open", icon="➡️", use_container_width=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        for icon, title, desc, path in FEATURES_COL1:
            render_nav_card(icon, title, desc, path)
    with col2:
        for icon, title, desc, path in FEATURES_COL2:
            render_nav_card(icon, title, desc, path)
    with col3:
        for icon, title, desc, path in FEATURES_COL3:
            render_nav_card(icon, title, desc, path)
else:
    section_title("What you get")
    colA, colB = st.columns([1.3, 1])
    with colA:
        st.markdown(
            """
            <div class="tf-card">
                <div class="tf-card-desc" style="font-size:0.98rem; line-height:1.7;">
                Welcome to <b>TalentForge AI</b> — an AI-powered career readiness platform that helps you:
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        chips([
            "📄 Resume parsing &amp; scoring",
            "🛠️ Resume builder",
            "🎤 Mock interviews",
            "🙂 On-camera presence",
            "🎙️ Speech &amp; delivery",
            "💻 Coding practice",
            "📊 Readiness dashboard",
        ])
        st.markdown(
            """
            <div style="margin-top:0.9rem;" class="tf-history-sub">
            All AI features run on <b>local, open-source models</b> — nothing is sent to an
            external API.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with colB:
        st.markdown(
            """
            <div class="tf-card" style="text-align:center;">
                <div class="tf-card-icon" style="font-size:2.4rem;">🔐</div>
                <div class="tf-card-title">Ready to start?</div>
                <div class="tf-card-desc">Log in or register to get started.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/0_Login.py", label="Log in / Register", icon="🔐", use_container_width=True)

st.markdown("---")
st.caption("TalentForge AI — built with Streamlit, spaCy, HuggingFace Transformers, "
           "sentence-transformers, FER, and Whisper.")