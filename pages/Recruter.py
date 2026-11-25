import streamlit as st

import database as db
from auth import require_role, current_user, render_auth_sidebar
from ml.job_matcher import rank_candidates
from theme import inject_theme, page_header, section_title, empty_state

st.set_page_config(page_title="Recruiter - TalentForge AI", page_icon="🧑‍💼", layout="wide")
inject_theme()
render_auth_sidebar()
require_role("recruiter", "admin")

user = current_user()
page_header(
    "🧑‍💼", "Recruiter Console",
    "Post a role and let semantic AI matching rank every candidate's resume against it — "
    "no manual keyword screening required.",
)

tab_post, tab_manage = st.tabs(["📝 Post a job", "🗂️ Manage jobs & candidates"])

with tab_post:
    with st.form("job_form"):
        title = st.text_input("Job title")
        location = st.text_input("Location", value="Remote")
        description = st.text_area("Job description", height=200)
        submitted = st.form_submit_button("Post job")

        if submitted:
            if not title or not description:
                st.warning("Title and description are required.")
            else:
                db.create_job(user["id"], title, description, location)
                st.success("Job posted.")
                st.rerun()

with tab_manage:
    jobs = db.get_jobs_by_recruiter(user["id"])
    if not jobs:
        empty_state("You haven't posted any jobs yet.", "🗂️")
    else:
        job_titles = {f"{j['title']} ({j['id']})": j for j in jobs}
        selected_label = st.selectbox("Select a job", list(job_titles.keys()))
        job = job_titles[selected_label]

        st.markdown(
            f"""
            <div class="tf-card">
                <div class="tf-history-sub">Location</div>
                <div class="tf-history-main" style="margin-bottom:0.6rem;">{job['location']}</div>
                <div class="tf-history-sub">Description</div>
                <div class="tf-history-main" style="font-weight:500;white-space:pre-wrap;">{job['description']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        section_title("Applicants")

        applications = db.get_applications_for_job(job["id"])
        if not applications:
            empty_state("No applicants yet.", "🧑‍💼")
        else:
            for app in applications:
                st.markdown(
                    f"""
                    <div class="tf-history-row">
                        <div>
                            <div class="tf-history-main">{app['full_name'] or app['username']}</div>
                            <div class="tf-history-sub">Status: {app['status']}</div>
                        </div>
                        <div class="tf-history-score">{app['match_score']}/100</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("---")
        section_title("Re-rank all candidates with resumes on file")

        if st.button("🔄 Run matching", use_container_width=True):
            with st.spinner("Scoring all candidate resumes against this job..."):
                candidate_texts = {}
                with db.get_connection() as conn:
                    rows = conn.execute(
                        """SELECT resumes.user_id, resumes.raw_text
                           FROM resumes
                           INNER JOIN (
                               SELECT user_id, MAX(uploaded_at) AS latest
                               FROM resumes GROUP BY user_id
                           ) latest_r
                           ON resumes.user_id = latest_r.user_id
                           AND resumes.uploaded_at = latest_r.latest"""
                    ).fetchall()
                    for r in rows:
                        candidate_texts[r["user_id"]] = r["raw_text"]

                ranked = rank_candidates(job["description"], candidate_texts)

                for user_id, score in ranked:
                    db.apply_to_job(job["id"], user_id, score)

            st.success(f"Matched against {len(candidate_texts)} candidate resumes.")
            st.rerun()
