import streamlit as st

from auth import (
    render_auth_sidebar,
    is_authenticated,
    current_user,
    login_user,
    register_user,
    logout_user,
)
from theme import inject_theme, page_header, auth_side_panel, safe_page_link

st.set_page_config(page_title="Login - TalentForge AI", page_icon="🔐", layout="wide")
inject_theme()
render_auth_sidebar()

if is_authenticated():
    user = current_user()
    page_header("✅", "You're already signed in", f"Signed in as **{user['username']}**.")

    col1, col2 = st.columns([1, 1])
    with col1:
        safe_page_link("app.py", "Go to home", icon="🏠", use_container_width=True)
    with col2:
        if st.button("🚪 Log out", use_container_width=True):
            logout_user()
            st.rerun()

else:
    page_header("🔐", "Welcome back", "Log in or create a free account to unlock the full suite.")

    with st.container(border=True):
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            auth_side_panel()

        with col2:
            st.markdown(
                """
                <div style="padding:2.2rem 1.6rem 0.4rem 1.6rem;">
                    <div class="tf-auth-form-title">Access your account</div>
                    <div class="tf-auth-form-sub">It only takes a few seconds.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.container():
                st.markdown('<div style="padding:0 1.6rem 2rem 1.6rem;">', unsafe_allow_html=True)
                tab_login, tab_register = st.tabs(["🔑 Log in", "✨ Register"])

                with tab_login:
                    with st.form("login_form", border=False):
                        u = st.text_input("Username", key="login_username")
                        p = st.text_input("Password", type="password", key="login_password")
                        submitted = st.form_submit_button("Log in", type="primary", use_container_width=True)
                    if submitted:
                        ok, msg = login_user(u.strip(), p)
                        st.success(msg) if ok else st.error(msg)
                        if ok:
                            st.rerun()

                with tab_register:
                    with st.form("register_form", border=False):
                        ru = st.text_input("Username", key="reg_username")
                        re_ = st.text_input("Email", key="reg_email")
                        rp = st.text_input("Password", type="password", key="reg_password")
                        rrole = st.selectbox("I am a", ["candidate", "recruiter"], key="reg_role")
                        rname = st.text_input("Full name", key="reg_fullname")
                        submitted = st.form_submit_button("Register", type="primary", use_container_width=True)
                    if submitted:
                        ok, msg = register_user(ru.strip(), re_.strip(), rp, rrole, rname.strip())
                        if ok:
                            st.success(msg)
                        else:
                            st.error(msg)
                st.markdown("</div>", unsafe_allow_html=True)

    st.caption("🔒 Passwords are hashed locally with bcrypt — nothing is ever sent to an external service.")