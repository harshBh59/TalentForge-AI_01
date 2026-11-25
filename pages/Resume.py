import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from utils.helpers import extract_text_from_upload
from nlp.resume_parser import parse_resume
from ml.resume_scorer import score_resume, score_breakdown
from theme import inject_theme, page_header, section_title, empty_state, chips

st.set_page_config(page_title="Resume - TalentForge AI", page_icon="📄", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header(
    "📄", "Resume Analyzer",
    "Upload a PDF, DOCX, or TXT resume to get an instant, explainable score — "
    "parsing and scoring both run locally on your machine.",
)

uploaded_file = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])

if uploaded_file is not None:
    with st.spinner("Extracting text..."):
        try:
            raw_text = extract_text_from_upload(uploaded_file)
        except ValueError as e:
            st.error(str(e))
            st.stop()

    if not raw_text.strip():
        st.error("Couldn't extract any text from that file — is it a scanned image?")
        st.stop()

    with st.spinner("Parsing with spaCy..."):
        parsed = parse_resume(raw_text)

    with st.spinner("Scoring..."):
        score, feedback = score_resume(parsed)
        breakdown = score_breakdown(parsed)

    db.save_resume(user["id"], uploaded_file.name, raw_text, parsed["skills"], score, feedback)

    st.success("Resume analyzed and saved.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Overall Score", f"{score}/100")

        section_title("Score breakdown")
        for label, pct in breakdown.items():
            st.progress(min(pct / 100, 1.0), text=f"{label}: {pct:.0f}%")

        section_title("Detected contact info")
        st.markdown(
            f"""
            <div class="tf-card">
                <div class="tf-history-sub">Name</div>
                <div class="tf-history-main" style="margin-bottom:0.5rem;">{parsed['name'] or 'Not detected'}</div>
                <div class="tf-history-sub">Email</div>
                <div class="tf-history-main" style="margin-bottom:0.5rem;">{parsed['email'] or 'Not detected'}</div>
                <div class="tf-history-sub">Phone</div>
                <div class="tf-history-main">{parsed['phone'] or 'Not detected'}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        section_title("Feedback")
        st.write(feedback)
        section_title("Detected skills")
        if parsed["skills"]:
            chips(parsed["skills"])
        else:
            st.write("No recognized skills found.")

    with st.expander("View parsed sections"):
        for section, content in parsed["sections"].items():
            st.markdown(f"**{section.title()}**")
            st.text(content[:1000])

st.markdown("---")
section_title("History")

resumes = db.get_resumes_by_user(user["id"])
if resumes:
    for r in resumes:
        st.markdown(
            f"""
            <div class="tf-history-row">
                <div>
                    <div class="tf-history-main">📄 {r['filename']}</div>
                    <div class="tf-history-sub">{r['uploaded_at'][:19]}</div>
                </div>
                <div class="tf-history-score">{r['score']}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
    empty_state("No resumes uploaded yet.", "📄")
