import pandas as pd
import plotly.express as px
import streamlit as st

import database as db
from auth import require_role, current_user, render_auth_sidebar
from theme import inject_theme, page_header, section_title, empty_state

st.set_page_config(page_title="Analytics - TalentForge AI", page_icon="📈", layout="wide")
inject_theme()
render_auth_sidebar()
require_role("recruiter", "admin")

user = current_user()
page_header(
    "📈", "Recruiting Analytics",
    "A hiring-funnel view across every job you've posted — applicant volume, match-score "
    "distribution, and your top-ranked candidates at a glance.",
)

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color="#E4E2FF"),
    colorway=["#7C5CFF", "#22D3EE", "#FF7AD9", "#5B8CFF", "#B389FF"],
    margin=dict(t=20, l=10, r=10, b=10),
)

jobs = db.get_jobs_by_recruiter(user["id"])

if not jobs:
    empty_state("Post a job to start seeing analytics.", "📭")
    st.stop()

all_apps = []
for job in jobs:
    for app in db.get_applications_for_job(job["id"]):
        app["job_title"] = job["title"]
        all_apps.append(app)

c1, c2, c3 = st.columns(3)
c1.metric("Open jobs", len(jobs))
c2.metric("Total applicants", len(all_apps))
avg_match = round(sum(a["match_score"] or 0 for a in all_apps) / len(all_apps), 1) if all_apps else 0
c3.metric("Avg. match score", f"{avg_match}/100" if all_apps else "—")

st.markdown("---")

if all_apps:
    df = pd.DataFrame(all_apps)

    col1, col2 = st.columns(2)
    with col1:
        section_title("Applicants per job")
        counts = df.groupby("job_title").size().reset_index(name="applicants")
        fig = px.bar(counts, x="job_title", y="applicants")
        fig.update_traces(marker_line_width=0)
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_title("Match score distribution")
        fig = px.histogram(df, x="match_score", nbins=20)
        fig.update_traces(marker_line_width=0)
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

    section_title("Application status breakdown")
    status_counts = df["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    fig = px.pie(status_counts, names="status", values="count", hole=0.45)
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    section_title("Top candidates across all jobs")
    top = df.sort_values("match_score", ascending=False).head(10)
    st.dataframe(
        top[["job_title", "username", "full_name", "match_score", "status"]],
        use_container_width=True,
    )
else:
    empty_state("No applicants yet — run matching from the Recruiter page.", "🧑\u200d💼")
