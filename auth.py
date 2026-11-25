"""
Authentication for TalentForge AI.
Handles registration, email/password login, Google OAuth login, logout,
and Streamlit session-state helpers every page uses to gate access.
"""

from urllib.parse import urlencode
import bcrypt
import streamlit as st

import database as db
from theme import sidebar_brand, sidebar_user_card, sidebar_footer, safe_page_link


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def register_user(username, email, password, role="candidate", full_name=""):
    username = (username or "").strip()
    email = (email or "").strip().lower()
    full_name = (full_name or "").strip()

    if not username or not email or not password:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if db.get_user_by_username(username):
        return False, "Username already taken."
    if hasattr(db, "get_user_by_email") and db.get_user_by_email(email):
        return False, "An account with this email already exists."

    try:
        db.create_user(username, email, hash_password(password), role, full_name)
        return True, "Account created. Please log in."
    except Exception as e:
        return False, f"Could not create account: {e}"


def login_user(username, password):
    username = (username or "").strip()
    user = db.get_user_by_username(username)
    if not user:
        return False, "No account with that username."
    if not user.get("password_hash"):
        return False, "This account uses Google Sign-In. Please continue with Google."
    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password."
    st.session_state["user"] = user
    return True, "Logged in successfully."


def _make_unique_username(email: str, name: str = "") -> str:
    base = (email.split("@")[0] if email else name or "google_user").lower()
    base = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in base).strip("_") or "user"
    candidate = base
    counter = 1
    while db.get_user_by_username(candidate):
        candidate = f"{base}_{counter}"
        counter += 1
    return candidate


def login_with_google_profile(google_sub: str, email: str, full_name: str = "", default_role: str = "candidate"):
    """
    Finds or creates a local user for a verified Google account and stores it
    in st.session_state['user'].
    """
    email = (email or "").strip().lower()
    if not email:
        return False, "Google account did not return an email address."

    user = None
    if hasattr(db, "get_user_by_google_sub") and google_sub:
        user = db.get_user_by_google_sub(google_sub)
    if not user and hasattr(db, "get_user_by_email"):
        user = db.get_user_by_email(email)

    if not user:
        username = _make_unique_username(email, full_name)
        if hasattr(db, "create_google_user"):
            db.create_google_user(
                username=username,
                email=email,
                google_sub=google_sub,
                role=default_role,
                full_name=full_name or username,
            )
        else:
            # Fallback if you haven't added a dedicated Google helper in database.py yet
            db.create_user(username, email, "", default_role, full_name or username)

        user = (
            db.get_user_by_email(email)
            if hasattr(db, "get_user_by_email")
            else db.get_user_by_username(username)
        )

    if not user:
        return False, "Could not load user profile after Google sign-in."

    st.session_state["user"] = user
    return True, "Signed in with Google."


def google_auth_url(state: str = "talentforge_oauth") -> str | None:
    """Builds a Google OAuth 2.0 consent URL using [google_oauth] in st.secrets."""
    google_cfg = st.secrets.get("google_oauth")
    if not google_cfg:
        return None
    params = {
        "client_id": google_cfg["client_id"],
        "redirect_uri": google_cfg["redirect_uri"],
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state,
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


def handle_google_callback():
    """
    Exchanges ?code=... from Google redirect for tokens and logs the user in.
    Call this near the top of pages/0_Login.py (or app.py).
    """
    code = st.query_params.get("code")
    if not code:
        return False, None

    google_cfg = st.secrets.get("google_oauth")
    if not google_cfg:
        return False, "Missing [google_oauth] configuration in secrets."

    try:
        from google_auth_oauthlib.flow import Flow

        client_config = {
            "web": {
                "client_id": google_cfg["client_id"],
                "client_secret": google_cfg["client_secret"],
                "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [google_cfg["redirect_uri"]],
            }
        }
        flow = Flow.from_client_config(
            client_config,
            scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
            redirect_uri=google_cfg["redirect_uri"],
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        # Fetch userinfo from Google
        import requests
        resp = requests.get(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {creds.token}"},
            timeout=10,
        )
        resp.raise_for_status()
        info = resp.json()

        # Clear OAuth query params so refreshes don't re-trigger token exchange
        st.query_params.clear()
        return login_with_google_profile(
            google_sub=info.get("sub", ""),
            email=info.get("email", ""),
            full_name=info.get("name", ""),
        )
    except Exception as e:
        st.query_params.clear()
        return False, f"Google sign-in failed: {e}"


def logout_user():
    st.session_state.pop("user", None)
    # If using native Streamlit OIDC st.login("google"), also call st.logout() where appropriate


def current_user():
    return st.session_state.get("user")


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


def require_login():
    """Call at the top of any page that needs a logged-in user."""
    if not is_authenticated():
        st.warning("Please log in to access this section.")
        safe_page_link("pages/0_Login.py", "Go to Login / Register", icon="🔐")
        st.stop()


def require_role(*roles):
    require_login()
    user = current_user()
    if user.get("role") not in roles:
        st.error(f"This page is restricted to: {', '.join(roles)}.")
        st.stop()


def render_auth_sidebar():
    """Small sidebar widget: brand + user card / logout, or a CTA to the Login page."""
    with st.sidebar:
        sidebar_brand()

        if is_authenticated():
            user = current_user()
            sidebar_user_card(user["username"], user["role"], user.get("full_name", ""))
            if st.button("🚪 Log out", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            st.markdown(
                '<div class="tf-sb-tagline">✨ Sign in to unlock every tool in the suite — '
                "resume scoring, mock interviews, voice &amp; emotion analysis, and more.</div>",
                unsafe_allow_html=True,
            )
            safe_page_link("pages/0_Login.py", "Log in / Register", icon="🔐", use_container_width=True)

        sidebar_footer()