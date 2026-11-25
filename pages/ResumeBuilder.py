import streamlit as st

import database as db
from auth import require_login, current_user, render_auth_sidebar
from utils.resume_doc_builder import build_resume_docx, build_resume_plain_text
from nlp.resume_parser import parse_resume
from ml.resume_scorer import score_resume
from theme import inject_theme, page_header, section_title

st.set_page_config(page_title="Resume Builder - TalentForge AI", page_icon="🛠️", layout="wide")
inject_theme()
render_auth_sidebar()
require_login()

user = current_user()
page_header(
    "🛠️", "Resume Builder",
    "Fill in the sections below and generate a polished, formatted resume — no file "
    "upload needed, and everything is scored locally against the same rubric used "
    "in Resume Analyzer.",
)


def _init_state():
    if "builder_experience" not in st.session_state:
        st.session_state["builder_experience"] = [
            {"title": "", "company": "", "location": "", "start": "", "end": "", "bullets": ""}
        ]
    if "builder_education" not in st.session_state:
        st.session_state["builder_education"] = [
            {"degree": "", "institution": "", "location": "", "start": "", "end": "", "details": ""}
        ]


_init_state()

# ---------------- Basic info ----------------
section_title("Basic information")
c1, c2 = st.columns(2)
with c1:
    full_name = st.text_input("Full name", value=user.get("full_name") or "")
    email = st.text_input("Email", value=user.get("email") or "")
    phone = st.text_input("Phone")
with c2:
    location = st.text_input("Location (city, state/country)")
    linkedin = st.text_input("LinkedIn / portfolio URL")

section_title("Summary")
summary = st.text_area(
    "A 2-3 sentence professional summary",
    value=user.get("bio") or "",
    height=100,
)

section_title("Skills")
skills_text = st.text_input("Comma-separated list of skills", placeholder="Python, SQL, Communication, ...")
skills = [s.strip() for s in skills_text.split(",") if s.strip()]

# ---------------- Experience ----------------
section_title("Experience")

for i, entry in enumerate(st.session_state["builder_experience"]):
    with st.expander(f"Experience #{i + 1}: {entry['title'] or 'New entry'}", expanded=True):
        c1, c2 = st.columns(2)
        entry["title"] = c1.text_input("Job title", value=entry["title"], key=f"exp_title_{i}")
        entry["company"] = c2.text_input("Company", value=entry["company"], key=f"exp_company_{i}")

        c3, c4, c5 = st.columns(3)
        entry["location"] = c3.text_input("Location", value=entry["location"], key=f"exp_loc_{i}")
        entry["start"] = c4.text_input("Start date", value=entry["start"], key=f"exp_start_{i}")
        entry["end"] = c5.text_input("End date", value=entry["end"], key=f"exp_end_{i}")

        entry["bullets"] = st.text_area(
            "Achievements / responsibilities (one per line)",
            value=entry["bullets"], height=100, key=f"exp_bullets_{i}",
        )

        if len(st.session_state["builder_experience"]) > 1:
            if st.button("Remove this entry", key=f"remove_exp_{i}"):
                st.session_state["builder_experience"].pop(i)
                st.rerun()

if st.button("➕ Add another experience entry", use_container_width=True):
    st.session_state["builder_experience"].append(
        {"title": "", "company": "", "location": "", "start": "", "end": "", "bullets": ""}
    )
    st.rerun()

# ---------------- Education ----------------
section_title("Education")

for i, entry in enumerate(st.session_state["builder_education"]):
    with st.expander(f"Education #{i + 1}: {entry['degree'] or 'New entry'}", expanded=True):
        c1, c2 = st.columns(2)
        entry["degree"] = c1.text_input("Degree / program", value=entry["degree"], key=f"edu_degree_{i}")
        entry["institution"] = c2.text_input("Institution", value=entry["institution"], key=f"edu_inst_{i}")

        c3, c4, c5 = st.columns(3)
        entry["location"] = c3.text_input("Location", value=entry["location"], key=f"edu_loc_{i}")
        entry["start"] = c4.text_input("Start date", value=entry["start"], key=f"edu_start_{i}")
        entry["end"] = c5.text_input("End date", value=entry["end"], key=f"edu_end_{i}")

        entry["details"] = st.text_input(
            "Extra details (GPA, honors, relevant coursework)",
            value=entry["details"], key=f"edu_details_{i}",
        )

        if len(st.session_state["builder_education"]) > 1:
            if st.button("Remove this entry", key=f"remove_edu_{i}"):
                st.session_state["builder_education"].pop(i)
                st.rerun()

if st.button("➕ Add another education entry", use_container_width=True):
    st.session_state["builder_education"].append(
        {"degree": "", "institution": "", "location": "", "start": "", "end": "", "details": ""}
    )
    st.rerun()

# ---------------- Certifications ----------------
section_title("Certifications (optional)")
certs_text = st.text_area("One per line", height=80)
certifications = [c.strip() for c in certs_text.splitlines() if c.strip()]

# ---------------- Generate ----------------
st.markdown("---")

if st.button("✨ Generate resume", type="primary", use_container_width=True):
    if not full_name.strip():
        st.warning("Add your full name before generating.")
    else:
        data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "location": location,
            "linkedin": linkedin,
            "summary": summary,
            "skills": skills,
            "experience": [
                {**e, "bullets": e["bullets"].splitlines()}
                for e in st.session_state["builder_experience"]
            ],
            "education": st.session_state["builder_education"],
            "certifications": certifications,
        }

        docx_bytes = build_resume_docx(data)
        plain_text = build_resume_plain_text(data)

        st.session_state["builder_last_docx"] = docx_bytes
        st.session_state["builder_last_text"] = plain_text
        st.success("Resume generated.")

if "builder_last_docx" in st.session_state:
    st.download_button(
        "⬇️ Download as .docx",
        data=st.session_state["builder_last_docx"],
        file_name=f"{(full_name or 'resume').replace(' ', '_')}_resume.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    with st.expander("Preview plain-text content"):
        st.text(st.session_state["builder_last_text"])

    section_title("Quick self-check score")
    st.caption("Runs the generated resume through the same scorer used in Resume Analyzer.")

    if st.button("🧮 Score this resume", use_container_width=True):
        with st.spinner("Parsing and scoring..."):
            parsed = parse_resume(st.session_state["builder_last_text"])
            score, feedback = score_resume(parsed)

        st.metric("Score", f"{score}/100")
        st.write(feedback)

        if st.button("💾 Save to my resume history", use_container_width=True):
            db.save_resume(
                user["id"],
                f"{full_name}_builder_resume.docx",
                st.session_state["builder_last_text"],
                parsed["skills"], score, feedback,
            )
            st.success("Saved — it'll now show up in Resume Analyzer, Dashboard, and Recruiter matching.")
