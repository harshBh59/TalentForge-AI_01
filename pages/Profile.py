import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from theme import inject_theme, page_header, section_title

st.set_page_config(page_title="Profile - TalentForge AI", page_icon="👤", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header("👤", "My Profile", "Keep your details current so every tool personalizes to you.")

col1, col2 = st.columns([1, 2])

with col1:
    section_title("Account")
    st.markdown(
        f"""
        <div class="tf-card">
            <div class="tf-history-sub">Username</div>
            <div class="tf-history-main" style="margin-bottom:0.6rem;">{user['username']}</div>
            <div class="tf-history-sub">Email</div>
            <div class="tf-history-main" style="margin-bottom:0.6rem;">{user['email']}</div>
            <div class="tf-history-sub">Role</div>
            <span class="tf-chip">{user['role']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    section_title("Edit profile")
    with st.form("profile_form"):
        full_name = st.text_input("Full name", value=user.get("full_name") or "")
        target_role = st.text_input(
            "Target role (e.g. software engineer, data analyst, product manager)",
            value=user.get("target_role") or "",
        )
        bio = st.text_area("Short bio", value=user.get("bio") or "", height=120)
        submitted = st.form_submit_button("Save changes")

        if submitted:
            db.update_user_profile(user["id"], full_name, target_role, bio)
            st.session_state["user"] = db.get_user_by_id(user["id"])
            st.success("Profile updated.")
            st.rerun()

st.markdown("---")
section_title("Snapshot")

resumes = db.get_resumes_by_user(user["id"])
interviews = db.get_interview_history(user["id"])
emotions = db.get_emotion_history(user["id"])

c1, c2, c3 = st.columns(3)
c1.metric("Resumes uploaded", len(resumes))
c2.metric("Interview sessions", len(interviews))
c3.metric("Emotion checks", len(emotions))

if resumes:
    st.info(f"Latest resume score: **{resumes[0]['score']}/100**")
