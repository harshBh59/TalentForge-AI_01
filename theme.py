"""
Premium visual theme for TalentForge AI.

This module is PURE PRESENTATION. It only injects CSS and renders small
HTML snippets around values that pages already compute. It never touches
auth, database, ml, nlp, speech, or vision logic — every page still calls
the exact same functions, with the exact same arguments, in the exact
same order. Import and call `inject_theme()` once near the top of every
page (right after `st.set_page_config(...)`), then optionally use the
helper components below for headers, empty-states, badges, and cards.
"""

import streamlit as st

# --------------------------------------------------------------------------
# Palette
# --------------------------------------------------------------------------
ACCENT = "#7C5CFF"        # primary violet
ACCENT_2 = "#22D3EE"      # cyan
ACCENT_3 = "#FF7AD9"      # pink
BG_DEEP = "#07070F"
BG_PANEL = "#11111C"


def inject_theme() -> None:
    """Inject the global premium CSS. Call once per page, after set_page_config."""
    st.markdown(
        """
    <style>
    :root{
        --accent:#7C5CFF;
        --accent-2:#22D3EE;
        --accent-3:#FF7AD9;
        --bg-deep:#07070F;
        --bg-panel:rgba(255,255,255,0.035);
        --border-soft:rgba(255,255,255,0.09);
        --text-dim:#9CA3C0;
    }

    html, body, [class*="css"]{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
    }

    h1,h2,h3,h4,h5,h6, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif !important;
        letter-spacing:-0.02em;
    }

    /* ---------------- App background ---------------- */
    [data-testid="stAppViewContainer"]{
        background:
            radial-gradient(1200px 600px at 8% -10%, rgba(124,92,255,0.20), transparent 60%),
            radial-gradient(1000px 700px at 110% 10%, rgba(34,211,238,0.14), transparent 55%),
            radial-gradient(900px 500px at 50% 120%, rgba(255,122,217,0.10), transparent 55%),
            var(--bg-deep);
        background-attachment:fixed;
    }
    [data-testid="stHeader"]{
        background:rgba(7,7,15,0.35) !important;
        backdrop-filter:blur(10px);
        border-bottom:1px solid rgba(255,255,255,0.05);
    }
    .main .block-container{
        padding-top:2rem;
        padding-bottom:4rem;
        max-width:1180px;
        animation:tf-fade-up .55s cubic-bezier(.16,1,.3,1) both;
    }

    @keyframes tf-fade-up{
        from{opacity:0; transform:translateY(14px);}
        to{opacity:1; transform:translateY(0);}
    }
    @keyframes tf-fade-in{
        from{opacity:0;} to{opacity:1;}
    }
    @keyframes tf-glow-pulse{
        0%,100%{box-shadow:0 0 0 0 rgba(124,92,255,0.35);}
        50%{box-shadow:0 0 0 8px rgba(124,92,255,0);}
    }
    @keyframes tf-shimmer{
        0%{background-position:0% 50%;}
        100%{background-position:200% 50%;}
    }
    @keyframes tf-float{
        0%,100%{transform:translateY(0px);}
        50%{transform:translateY(-6px);}
    }

    @keyframes tf-border-flow{
        0%{background-position:0% 0%;}
        100%{background-position:200% 0%;}
    }
    @keyframes tf-pulse-dot{
        0%{box-shadow:0 0 0 0 rgba(52,222,152,0.55);}
        70%{box-shadow:0 0 0 6px rgba(52,222,152,0);}
        100%{box-shadow:0 0 0 0 rgba(52,222,152,0);}
    }
    @keyframes tf-blob-drift{
        0%,100%{transform:translate(0,0) scale(1);}
        33%{transform:translate(10px,-14px) scale(1.08);}
        66%{transform:translate(-8px,10px) scale(0.95);}
    }
    @keyframes tf-avatar-spin{
        from{transform:rotate(0deg);} to{transform:rotate(360deg);}
    }
    @keyframes tf-slide-in{
        from{opacity:0; transform:translateX(-10px);}
        to{opacity:1; transform:translateX(0);}
    }

    /* ---------------- Sidebar ---------------- */
    [data-testid="stSidebar"]{
        background:
            radial-gradient(420px 260px at -10% -10%, rgba(124,92,255,0.30), transparent 60%),
            radial-gradient(360px 320px at 120% 30%, rgba(34,211,238,0.18), transparent 60%),
            radial-gradient(300px 260px at 10% 115%, rgba(255,122,217,0.14), transparent 60%),
            linear-gradient(180deg, rgba(19,17,34,0.99), rgba(8,8,15,0.99));
        border-right:1px solid rgba(255,255,255,0.07);
        box-shadow:6px 0 40px -20px rgba(124,92,255,0.35);
        position:relative;
        overflow:visible;
    }
    /* animated shimmering top border for the whole sidebar */
    [data-testid="stSidebar"]::before{
        content:"";
        position:absolute; top:0; left:0; right:0; height:3px;
        background:linear-gradient(90deg, var(--accent), var(--accent-2), var(--accent-3), var(--accent));
        background-size:250% 100%;
        animation:tf-border-flow 5s linear infinite;
        z-index:5;
    }
    [data-testid="stSidebar"] .block-container{ padding-top:1.5rem; position:relative; z-index:1; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{
        color:#fff;
    }
    [data-testid="stSidebar"] hr{
        border:none !important;
        height:1px;
        background:linear-gradient(90deg, transparent, rgba(124,92,255,0.55), rgba(34,211,238,0.4), transparent) !important;
        margin:1.1rem 0 !important;
    }
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] .stCaption, [data-testid="stSidebar"] p{
        color:#C7C4E6;
    }

    /* Brand block */
    .tf-sb-brand{
        display:flex; align-items:center; gap:0.7rem;
        margin-bottom:1.2rem;
        animation:tf-slide-in .45s cubic-bezier(.16,1,.3,1) both;
    }
    .tf-sb-logo{
        width:42px; height:42px; border-radius:13px;
        display:flex; align-items:center; justify-content:center;
        font-size:1.35rem;
        background:linear-gradient(135deg, var(--accent), var(--accent-2));
        box-shadow:0 4px 18px -4px rgba(124,92,255,0.7);
        position:relative;
        flex-shrink:0;
    }
    .tf-sb-logo::after{
        content:"";
        position:absolute; inset:-4px;
        border-radius:16px;
        border:1.5px solid rgba(124,92,255,0.5);
        animation:tf-glow-pulse 2.6s ease-in-out infinite;
    }
    .tf-sb-brand-text{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; font-weight:800; font-size:1.12rem; line-height:1.15;
        background:linear-gradient(90deg,#fff,var(--accent-2) 60%,var(--accent-3));
        background-size:200% auto;
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        animation:tf-shimmer 7s linear infinite;
    }
    .tf-sb-brand-sub{ font-size:0.7rem; color:var(--text-dim); letter-spacing:0.04em; text-transform:uppercase; margin-top:1px;}

    /* User card with avatar + pulsing status */
    .tf-sb-usercard{
        display:flex; align-items:center; gap:0.75rem;
        background:linear-gradient(160deg, rgba(255,255,255,0.06), rgba(255,255,255,0.015));
        border:1px solid rgba(255,255,255,0.1);
        border-radius:16px;
        padding:0.8rem 0.9rem;
        margin-bottom:0.85rem;
        position:relative;
        transition:all .25s ease;
        animation:tf-slide-in .5s cubic-bezier(.16,1,.3,1) both;
    }
    .tf-sb-usercard:hover{
        border-color:rgba(124,92,255,0.55);
        box-shadow:0 12px 28px -14px rgba(124,92,255,0.55);
        transform:translateY(-2px);
    }
    .tf-sb-avatar{
        position:relative;
        width:44px; height:44px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; font-weight:800; font-size:1.05rem; color:#fff;
        flex-shrink:0;
    }
    .tf-sb-avatar-ring{
        position:absolute; inset:-3px; border-radius:50%;
        background:conic-gradient(from 0deg, var(--accent), var(--accent-2), var(--accent-3), var(--accent));
        animation:tf-avatar-spin 6s linear infinite;
        z-index:0;
    }
    .tf-sb-avatar-inner{
        position:absolute; inset:2.5px; border-radius:50%;
        display:flex; align-items:center; justify-content:center;
        background:#141225; z-index:1;
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; font-weight:800; color:#fff;
    }
    .tf-sb-status-dot{
        position:absolute; bottom:0; right:0;
        width:11px; height:11px; border-radius:50%;
        background:#34DE98; border:2px solid #141225;
        animation:tf-pulse-dot 2s infinite; z-index:2;
    }
    .tf-sb-username{ font-weight:700; color:#fff; font-size:0.94rem; line-height:1.2;}
    .tf-sb-role{
        display:inline-block; margin-top:0.3rem;
        font-size:0.66rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em;
        padding:0.15rem 0.55rem; border-radius:999px; color:#fff;
        background:linear-gradient(90deg, rgba(124,92,255,0.55), rgba(34,211,238,0.4));
    }

    .tf-sb-tagline{
        font-size:0.82rem; color:var(--text-dim); line-height:1.5;
        margin-bottom:0.9rem;
        animation:tf-slide-in .55s cubic-bezier(.16,1,.3,1) both;
    }

    .tf-sb-footer{
        margin-top:1.4rem; padding-top:1rem;
        border-top:1px solid rgba(255,255,255,0.08);
        display:flex; align-items:center; gap:0.4rem;
        font-size:0.72rem; color:var(--text-dim);
    }
    .tf-sb-footer .tf-dot{
        width:6px; height:6px; border-radius:50%;
        background:var(--accent-2); animation:tf-pulse-dot 2.2s infinite;
    }

    /* Sidebar page navigation (auto-generated multipage links) */
    [data-testid="stSidebarNav"]{
        padding-top:0.4rem;
    }
    [data-testid="stSidebarNav"] ul{ padding-left:0; }
    [data-testid="stSidebarNavLink"], [data-testid="stSidebarNav"] a{
        border-radius:12px !important;
        margin:2px 0 !important;
        transition:all .22s cubic-bezier(.16,1,.3,1) !important;
        color:#C7C4E6 !important;
        border:1px solid transparent !important;
    }
    [data-testid="stSidebarNavLink"]:hover, [data-testid="stSidebarNav"] a:hover{
        background:rgba(124,92,255,0.14) !important;
        border-color:rgba(124,92,255,0.4) !important;
        transform:translateX(4px);
        color:#fff !important;
    }
    [data-testid="stSidebarNavLink"][aria-current="page"], [data-testid="stSidebarNav"] a[aria-current="page"]{
        background:linear-gradient(90deg, rgba(124,92,255,0.30), rgba(34,211,238,0.10)) !important;
        border-color:rgba(124,92,255,0.55) !important;
        box-shadow:inset 3px 0 0 var(--accent-2);
        color:#fff !important;
        font-weight:700 !important;
    }
    [data-testid="stSidebarNavSeparator"]{
        background:linear-gradient(90deg, transparent, rgba(124,92,255,0.4), transparent) !important;
    }

    /* Sidebar-local buttons feel more compact + glowy */
    [data-testid="stSidebar"] .stButton > button{ width:100%; }
    [data-testid="stSidebar"] [data-testid="stTabs"] [data-baseweb="tab"]{ padding:8px 12px; font-size:0.85rem; }

    /* ---------------- Buttons ---------------- */
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button{
        border-radius:12px !important;
        border:1px solid rgba(255,255,255,0.12) !important;
        background:rgba(255,255,255,0.04) !important;
        color:#EDEBFF !important;
        font-weight:600 !important;
        padding:0.55rem 1.2rem !important;
        transition:all .25s cubic-bezier(.16,1,.3,1) !important;
        box-shadow:0 1px 2px rgba(0,0,0,0.4) !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover{
        transform:translateY(-2px) scale(1.01);
        border-color:rgba(124,92,255,0.6) !important;
        box-shadow:0 10px 24px -8px rgba(124,92,255,0.55) !important;
        color:#fff !important;
    }
    .stButton > button:active{ transform:translateY(0) scale(0.99); }

    button[kind="primary"], button[kind="primaryFormSubmit"]{
        background:linear-gradient(120deg, var(--accent), #5B8CFF 45%, var(--accent-2)) !important;
        background-size:200% 200% !important;
        border:none !important;
        color:#fff !important;
        animation:tf-shimmer 6s ease infinite;
    }
    button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover{
        box-shadow:0 12px 28px -8px rgba(124,92,255,0.75) !important;
        transform:translateY(-2px) scale(1.02);
    }

    /* ---------------- Inputs ---------------- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stNumberInput"] input{
        background:rgba(255,255,255,0.035) !important;
        border:1px solid var(--border-soft) !important;
        border-radius:10px !important;
        color:#F1F0FF !important;
        transition:all .2s ease;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus,
    div[data-testid="stNumberInput"] input:focus{
        border-color:var(--accent) !important;
        box-shadow:0 0 0 3px rgba(124,92,255,0.25) !important;
    }
    div[data-baseweb="select"] > div{
        background:rgba(255,255,255,0.035) !important;
        border-radius:10px !important;
        border:1px solid var(--border-soft) !important;
    }

    /* ---------------- Tabs ---------------- */
    [data-testid="stTabs"] [data-baseweb="tab-list"]{
        gap:6px;
        border-bottom:1px solid var(--border-soft);
    }
    [data-testid="stTabs"] [data-baseweb="tab"]{
        border-radius:10px 10px 0 0;
        color:var(--text-dim);
        font-weight:600;
        padding:10px 16px;
        transition:all .2s ease;
    }
    [data-testid="stTabs"] [data-baseweb="tab"]:hover{ color:#fff; background:rgba(255,255,255,0.04); }
    [data-testid="stTabs"] [aria-selected="true"]{
        color:#fff !important;
        background:linear-gradient(180deg, rgba(124,92,255,0.20), rgba(124,92,255,0.05));
        box-shadow:inset 0 -2px 0 var(--accent);
    }

    /* ---------------- Expander ---------------- */
    [data-testid="stExpander"]{
        background:rgba(255,255,255,0.03);
        border:1px solid var(--border-soft) !important;
        border-radius:14px !important;
        overflow:hidden;
        transition:border-color .2s ease;
    }
    [data-testid="stExpander"]:hover{ border-color:rgba(124,92,255,0.45) !important; }

    /* ---------------- Metrics ---------------- */
    div[data-testid="stMetric"]{
        background:linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015));
        border:1px solid var(--border-soft);
        border-radius:16px;
        padding:1rem 1.1rem 0.8rem 1.1rem;
        transition:all .25s cubic-bezier(.16,1,.3,1);
    }
    div[data-testid="stMetric"]:hover{
        transform:translateY(-3px);
        border-color:rgba(124,92,255,0.5);
        box-shadow:0 14px 30px -12px rgba(124,92,255,0.45);
    }
    div[data-testid="stMetricLabel"]{ color:var(--text-dim) !important; }
    div[data-testid="stMetricValue"]{
        background:linear-gradient(90deg, #fff, #C9C4FF);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    }

    /* ---------------- Alerts ---------------- */
    div[data-testid="stAlert"], div[data-testid="stNotification"]{
        border-radius:12px !important;
        border:1px solid var(--border-soft) !important;
        animation:tf-fade-in .35s ease both;
        backdrop-filter:blur(6px);
    }

    /* ---------------- Progress bars ---------------- */
    div[data-testid="stProgress"] > div > div{
        background:linear-gradient(90deg, var(--accent), var(--accent-2)) !important;
        border-radius:8px;
    }
    div[data-testid="stProgress"]{ border-radius:8px; overflow:hidden; }

    /* ---------------- Dataframe / tables ---------------- */
    div[data-testid="stDataFrame"]{
        border:1px solid var(--border-soft);
        border-radius:14px;
        overflow:hidden;
    }

    /* ---------------- File uploader / camera / audio ---------------- */
    div[data-testid="stFileUploaderDropzone"], div[data-testid="stCameraInput"] video{
        border-radius:14px !important;
    }
    div[data-testid="stFileUploaderDropzone"]{
        background:rgba(255,255,255,0.03) !important;
        border:1.5px dashed rgba(124,92,255,0.4) !important;
        transition:all .2s ease;
    }
    div[data-testid="stFileUploaderDropzone"]:hover{
        border-color:var(--accent) !important;
        background:rgba(124,92,255,0.06) !important;
    }

    /* ---------------- Divider ---------------- */
    hr{ border-color:var(--border-soft) !important; margin:1.6rem 0 !important; }

    /* ---------------- Scrollbar ---------------- */
    ::-webkit-scrollbar{ width:10px; height:10px; }
    ::-webkit-scrollbar-track{ background:transparent; }
    ::-webkit-scrollbar-thumb{
        background:linear-gradient(180deg, var(--accent), var(--accent-2));
        border-radius:8px;
    }

    /* ---------------- Custom TF components ---------------- */
    .tf-hero{
        position:relative;
        padding:2.6rem 2.4rem;
        border-radius:24px;
        margin-bottom:1.8rem;
        background:linear-gradient(135deg, rgba(124,92,255,0.16), rgba(34,211,238,0.08) 55%, rgba(255,122,217,0.10));
        border:1px solid rgba(255,255,255,0.09);
        overflow:hidden;
        animation:tf-fade-up .6s cubic-bezier(.16,1,.3,1) both;
    }
    .tf-hero::before{
        content:"";
        position:absolute; inset:-40% -10% auto auto;
        width:260px; height:260px; border-radius:50%;
        background:radial-gradient(circle, rgba(124,92,255,0.35), transparent 70%);
        animation:tf-float 7s ease-in-out infinite;
    }
    .tf-hero-icon{
        font-size:2.4rem;
        display:inline-block;
        animation:tf-float 4s ease-in-out infinite;
    }
    .tf-hero-title{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        font-size:2.1rem;
        font-weight:800;
        margin:0.35rem 0 0.35rem 0;
        background:linear-gradient(90deg, #fff 20%, var(--accent-2) 50%, var(--accent-3) 80%);
        background-size:200% auto;
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        animation:tf-shimmer 8s linear infinite;
    }
    .tf-hero-subtitle{
        color:var(--text-dim);
        font-size:1.02rem;
        max-width:640px;
        position:relative;
        z-index:1;
    }
    .tf-badge{
        display:inline-block;
        padding:0.28rem 0.75rem;
        font-size:0.72rem;
        font-weight:700;
        letter-spacing:0.04em;
        text-transform:uppercase;
        border-radius:999px;
        color:#fff;
        background:rgba(124,92,255,0.18);
        border:1px solid rgba(124,92,255,0.45);
        margin-bottom:0.9rem;
    }

    .tf-section-title{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        font-weight:700;
        font-size:1.28rem;
        margin:1.6rem 0 0.9rem 0;
        display:flex; align-items:center; gap:0.5rem;
        color:#F4F2FF;
    }
    .tf-section-title .tf-bar{
        width:5px; height:1.2rem; border-radius:4px;
        background:linear-gradient(180deg, var(--accent), var(--accent-2));
        display:inline-block;
    }

    .tf-card{
        position:relative;
        background:linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015));
        border:1px solid var(--border-soft);
        border-radius:18px;
        padding:1.3rem 1.35rem;
        margin-bottom:1rem;
        transition:all .3s cubic-bezier(.16,1,.3,1);
    }
    .tf-card:hover{
        transform:translateY(-5px);
        border-color:rgba(124,92,255,0.55);
        box-shadow:0 20px 40px -18px rgba(124,92,255,0.5);
    }
    .tf-card .tf-card-icon{ font-size:1.6rem; }
    .tf-card .tf-card-title{
        font-weight:700; font-size:1.02rem; margin:0.5rem 0 0.3rem 0; color:#fff;
    }
    .tf-card .tf-card-desc{ color:var(--text-dim); font-size:0.9rem; line-height:1.45; }
    .tf-card .tf-card-pill{
        position:absolute; top:1rem; right:1rem;
        font-size:0.65rem; font-weight:700; text-transform:uppercase;
        letter-spacing:.03em; color:var(--accent-2);
        background:rgba(34,211,238,0.12); border:1px solid rgba(34,211,238,0.35);
        padding:0.15rem 0.55rem; border-radius:999px;
    }

    .tf-empty{
        border:1px dashed var(--border-soft);
        border-radius:14px;
        padding:1.4rem;
        text-align:center;
        color:var(--text-dim);
        background:rgba(255,255,255,0.02);
    }

    .tf-history-row{
        display:flex; justify-content:space-between; align-items:center;
        gap:1rem;
        padding:0.7rem 0.95rem;
        border-radius:12px;
        border:1px solid var(--border-soft);
        background:rgba(255,255,255,0.02);
        margin-bottom:0.55rem;
        transition:all .2s ease;
    }
    .tf-history-row:hover{
        border-color:rgba(124,92,255,0.45);
        background:rgba(124,92,255,0.06);
        transform:translateX(3px);
    }
    .tf-history-main{ color:#F1F0FF; font-weight:600; font-size:0.92rem; }
    .tf-history-sub{ color:var(--text-dim); font-size:0.78rem; }
    .tf-history-score{
        font-weight:800; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
        background:linear-gradient(90deg, var(--accent-2), var(--accent));
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        white-space:nowrap;
    }

    .tf-chip{
        display:inline-block; padding:0.3rem 0.7rem; margin:0.15rem 0.25rem 0.15rem 0;
        border-radius:999px; font-size:0.78rem; font-weight:600;
        background:rgba(124,92,255,0.14); border:1px solid rgba(124,92,255,0.4);
        color:#E4E0FF;
        transition:all .2s ease;
    }
    .tf-chip:hover{ background:rgba(124,92,255,0.28); transform:translateY(-2px); }

    /* ---------------- Auth / Login page ---------------- */
    @keyframes tf-orb-drift{
        0%,100%{transform:translate(0,0) scale(1);}
        50%{transform:translate(-18px,22px) scale(1.12);}
    }
    @keyframes tf-orb-drift-2{
        0%,100%{transform:translate(0,0) scale(1);}
        50%{transform:translate(20px,-16px) scale(0.9);}
    }
    @keyframes tf-check-pop{
        0%{transform:scale(0.6); opacity:0;}
        60%{transform:scale(1.08); opacity:1;}
        100%{transform:scale(1);}
    }
    .tf-auth-wrap{
        position:relative;
        border-radius:26px;
        overflow:hidden;
        border:1px solid rgba(255,255,255,0.09);
        background:linear-gradient(135deg, rgba(255,255,255,0.045), rgba(255,255,255,0.01));
        animation:tf-fade-up .6s cubic-bezier(.16,1,.3,1) both;
        margin-bottom:1.5rem;
    }
    .tf-auth-grid{
        display:grid;
        grid-template-columns:1.05fr 1fr;
        min-height:460px;
    }
    @media (max-width:900px){ .tf-auth-grid{ grid-template-columns:1fr; } }
    .tf-auth-side{
        position:relative;
        padding:2.6rem 2.4rem;
        background:
            radial-gradient(360px 300px at 15% 10%, rgba(124,92,255,0.35), transparent 60%),
            radial-gradient(320px 280px at 90% 80%, rgba(34,211,238,0.25), transparent 60%),
            linear-gradient(160deg, rgba(124,92,255,0.14), rgba(10,9,20,0.4));
        display:flex; flex-direction:column; justify-content:center;
        overflow:hidden;
    }
    .tf-auth-side::before{
        content:"";
        position:absolute; width:200px; height:200px; border-radius:50%;
        top:-60px; left:-60px;
        background:radial-gradient(circle, rgba(124,92,255,0.45), transparent 70%);
        animation:tf-orb-drift 8s ease-in-out infinite;
    }
    .tf-auth-side::after{
        content:"";
        position:absolute; width:220px; height:220px; border-radius:50%;
        bottom:-70px; right:-50px;
        background:radial-gradient(circle, rgba(34,211,238,0.35), transparent 70%);
        animation:tf-orb-drift-2 9s ease-in-out infinite;
    }
    .tf-auth-brand{
        display:flex; align-items:center; gap:0.8rem; margin-bottom:1.4rem; position:relative; z-index:1;
    }
    .tf-auth-logo{
        width:52px; height:52px; border-radius:16px;
        display:flex; align-items:center; justify-content:center; font-size:1.7rem;
        background:linear-gradient(135deg, var(--accent), var(--accent-2));
        box-shadow:0 8px 24px -6px rgba(124,92,255,0.7);
        animation:tf-float 4s ease-in-out infinite;
    }
    .tf-auth-title{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; font-weight:800; font-size:1.9rem; line-height:1.15;
        background:linear-gradient(90deg,#fff, var(--accent-2) 55%, var(--accent-3));
        background-size:200% auto;
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        animation:tf-shimmer 8s linear infinite;
        position:relative; z-index:1;
        margin-bottom:0.6rem;
    }
    .tf-auth-desc{
        color:var(--text-dim); font-size:0.98rem; line-height:1.65; max-width:420px;
        position:relative; z-index:1; margin-bottom:1.3rem;
    }
    .tf-auth-feature{
        display:flex; align-items:center; gap:0.6rem;
        font-size:0.9rem; color:#E4E2FF; margin-bottom:0.65rem;
        position:relative; z-index:1;
        animation:tf-slide-in .5s cubic-bezier(.16,1,.3,1) both;
    }
    .tf-auth-feature .tf-check{
        width:22px; height:22px; border-radius:50%; flex-shrink:0;
        display:flex; align-items:center; justify-content:center;
        background:linear-gradient(135deg, var(--accent), var(--accent-2));
        font-size:0.72rem; font-weight:800; color:#fff;
        animation:tf-check-pop .5s cubic-bezier(.34,1.56,.64,1) both;
    }
    .tf-auth-form-side{
        padding:2.6rem 2.6rem;
        display:flex; flex-direction:column; justify-content:center;
        background:rgba(10,9,18,0.35);
    }
    .tf-auth-form-title{
        font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; font-weight:800; font-size:1.35rem; color:#fff;
        margin-bottom:0.25rem;
    }
    .tf-auth-form-sub{ color:var(--text-dim); font-size:0.88rem; margin-bottom:1.2rem; }

    /* Real st.container(border=True) used to host the Login/Register split card */
    div[data-testid="stVerticalBlockBorderWrapper"]{
        border-radius:26px !important;
        border:1px solid rgba(255,255,255,0.09) !important;
        background:linear-gradient(135deg, rgba(255,255,255,0.045), rgba(255,255,255,0.01)) !important;
        overflow:hidden;
        animation:tf-fade-up .6s cubic-bezier(.16,1,.3,1) both;
    }

    /* Home-page feature cards (bordered containers wrapping a page_link) get
       a hover lift so it's visually obvious the whole card is clickable. */
    div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPageLink"]){
        padding:0.4rem 0.2rem;
        transition:transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPageLink"]):hover{
        transform:translateY(-3px);
        border-color:rgba(124,92,255,0.45) !important;
        box-shadow:0 12px 28px rgba(124,92,255,0.18);
    }

    /* st.page_link styled as a clear call-to-action pill */
    [data-testid="stPageLink"]{
        border-radius:10px !important;
        font-weight:600 !important;
    }
    [data-testid="stPageLink"] p{
        color:var(--accent) !important;
        font-weight:600 !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def auth_side_panel() -> None:
    """Left-hand animated marketing panel for the dedicated Login/Register page."""
    st.markdown(
        """
        <div class="tf-auth-side">
            <div class="tf-auth-brand">
                <div class="tf-auth-logo">🧠</div>
            </div>
            <div class="tf-auth-title">Welcome to<br/>TalentForge AI</div>
            <div class="tf-auth-desc">
                Your all-in-one, privacy-first career readiness suite — every AI
                feature runs on local, open-source models.
            </div>
            <div class="tf-auth-feature"><span class="tf-check">✓</span> AI resume scoring &amp; builder</div>
            <div class="tf-auth-feature"><span class="tf-check">✓</span> Mock interviews with instant feedback</div>
            <div class="tf-auth-feature"><span class="tf-check">✓</span> Voice, emotion &amp; coding practice</div>
            <div class="tf-auth-feature"><span class="tf-check">✓</span> One dashboard to track it all</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    """Animated logo + wordmark block, shown at the top of the sidebar."""
    st.markdown(
        """
        <div class="tf-sb-brand">
            <div class="tf-sb-logo">🧠</div>
            <div>
                <div class="tf-sb-brand-text">TalentForge AI</div>
                <div class="tf-sb-brand-sub">Career Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _avatar_gradient(seed: str) -> str:
    """Deterministic two-color gradient for an avatar, derived from a name. Pure display helper."""
    hue = (sum(ord(c) for c in seed) * 37) % 360
    hue2 = (hue + 55) % 360
    return f"linear-gradient(135deg, hsl({hue},80%,62%), hsl({hue2},85%,58%))"


def sidebar_user_card(username: str, role: str, full_name: str = "") -> None:
    """Avatar + name + role card for a signed-in user."""
    label = (full_name or username or "?").strip()
    initials = "".join([p[0] for p in label.split()[:2]]).upper() or "?"
    gradient = _avatar_gradient(username or label)
    st.markdown(
        f"""
        <div class="tf-sb-usercard">
            <div class="tf-sb-avatar">
                <div class="tf-sb-avatar-ring"></div>
                <div class="tf-sb-avatar-inner" style="background:{gradient};">{initials}</div>
                <div class="tf-sb-status-dot"></div>
            </div>
            <div>
                <div class="tf-sb-username">{username}</div>
                <span class="tf-sb-role">{role}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_footer(text: str = "Runs on local, open-source AI") -> None:
    st.markdown(
        f"""
        <div class="tf-sb-footer">
            <span class="tf-dot"></span>{text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_page_link(page: str, label: str, icon: str = "", use_container_width: bool = False) -> None:
    """
    Same as st.page_link, but never crashes the page.
    st.page_link can raise if the app wasn't started from app.py (e.g. a page
    file under pages/ was launched directly as the entrypoint) — in that case
    we fall back to plain text instead of taking down the whole page.
    """
    try:
        st.page_link(page, label=label, icon=icon, use_container_width=use_container_width)
    except Exception:
        st.caption(f"{icon} {label} — open **app.py** (the app's home page) to navigate there.")

def hero(icon: str, title: str, subtitle: str = "", badge: str = "") -> None:
    """Big animated hero header for the home page."""
    badge_html = f'<div class="tf-badge">{badge}</div>' if badge else ""
    st.markdown(
        f"""
        <div class="tf-hero">
            {badge_html}
            <div class="tf-hero-icon">{icon}</div>
            <div class="tf-hero-title">{title}</div>
            <div class="tf-hero-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(icon: str, title: str, subtitle: str = "") -> None:
    """Compact animated header used at the top of every inner page."""
    st.markdown(
        f"""
        <div class="tf-hero" style="padding:1.5rem 1.8rem;">
            <div style="display:flex; align-items:center; gap:0.85rem;">
                <div class="tf-hero-icon" style="font-size:1.9rem;">{icon}</div>
                <div>
                    <div class="tf-hero-title" style="font-size:1.55rem; margin:0;">{title}</div>
                    {f'<div class="tf-hero-subtitle" style="font-size:0.92rem; margin-top:2px;">{subtitle}</div>' if subtitle else ''}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text: str) -> None:
    st.markdown(
        f'<div class="tf-section-title"><span class="tf-bar"></span>{text}</div>',
        unsafe_allow_html=True,
    )


def empty_state(text: str, icon: str = "✨") -> None:
    st.markdown(
        f'<div class="tf-empty">{icon}&nbsp;&nbsp;{text}</div>',
        unsafe_allow_html=True,
    )


def chips(items) -> None:
    """Render a list of strings as pill chips."""
    html = "".join(f'<span class="tf-chip">{i}</span>' for i in items)
    st.markdown(html, unsafe_allow_html=True)


def history_row(main: str, sub: str, score: str = "") -> None:
    score_html = f'<div class="tf-history-score">{score}</div>' if score else ""
    st.markdown(
        f"""
        <div class="tf-history-row">
            <div>
                <div class="tf-history-main">{main}</div>
                <div class="tf-history-sub">{sub}</div>
            </div>
            {score_html}
        </div>
        """,
        unsafe_allow_html=True,
    )