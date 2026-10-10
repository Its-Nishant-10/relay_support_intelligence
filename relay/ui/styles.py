from __future__ import annotations

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;600;700&display=swap');

        :root {
            --bg: #050505;
            --surface: #101010;
            --surface-muted: #171717;
            --border: #2a2a2a;
            --text: #f5f5f0;
            --muted: #a6a6a0;
            --accent: #f2c94c;
            --accent-soft: #332b12;
            --success: #62d18c;
            --success-soft: #102d1d;
            --warning: #f2c94c;
            --warning-soft: #332b12;
            --danger: #ef7777;
            --danger-soft: #351717;
            --radius: 8px;
        }

        html, body, [class*="css"], button, input, textarea, select {
            font-family: "Google Sans", Arial, sans-serif !important;
            color: var(--text);
        }
        body, .stApp, [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main,
        [data-testid="stMainBlockContainer"] {
            background: var(--bg) !important;
            color: var(--text) !important;
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] {
            background: var(--bg) !important;
            color: var(--text) !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        [data-testid="stHeader"] button,
        [data-testid="stToolbar"] button,
        [data-testid="stSidebar"] button {
            color: var(--text) !important;
            background: transparent !important;
            border-color: transparent !important;
        }
        [data-testid="stHeader"] button:hover,
        [data-testid="stToolbar"] button:hover,
        [data-testid="stSidebar"] button:hover {
            color: var(--accent) !important;
            background: var(--surface-muted) !important;
        }
        [data-testid="stIconMaterial"],
        [data-testid="stMainMenuButton"] svg,
        [data-testid="stSidebarCollapseButton"] svg {
            color: var(--text) !important;
            fill: currentColor !important;
            opacity: 1 !important;
        }
        [data-testid="stHeader"] button *,
        [data-testid="stSidebar"] button * {
            color: inherit !important;
        }
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background: #090909 !important;
            border-right: 1px solid var(--border);
        }
        [data-testid="stSidebarContent"] { padding: 1.1rem .85rem; }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
            color: var(--muted) !important;
        }

        .block-container {
            max-width: 1440px;
            padding: 4.5rem clamp(1rem, 4vw, 3rem) 3rem;
        }
        [data-testid="stMainBlockContainer"] {
            padding-top: 80px !important;
        }
        h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
            color: var(--text);
        }
        h1 { font-size: 2rem !important; font-weight: 600 !important; line-height: 1.15 !important; }
        h2 { font-size: 1.35rem !important; font-weight: 600 !important; }
        h3 { font-size: 1.05rem !important; font-weight: 600 !important; }
        p { line-height: 1.5; }
        [data-testid="stCaptionContainer"] p, .stCaption {
            color: var(--muted) !important;
        }

        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: .9rem 1rem;
        }
        [data-testid="stMetricLabel"] {
            color: var(--muted) !important;
            font-size: .75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: .05em;
        }
        [data-testid="stMetricValue"] {
            color: var(--text) !important;
            font-size: 1.6rem;
            font-weight: 600;
        }

        .stButton > button, .stDownloadButton > button {
            min-height: 2.4rem;
            border-radius: var(--radius);
            border: 1px solid var(--border);
            background: var(--surface-muted);
            color: var(--text) !important;
            font-weight: 600;
            box-shadow: none;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            border-color: var(--accent);
            color: var(--accent) !important;
        }
        .stButton > button p, .stDownloadButton > button p,
        .stButton > button span, .stDownloadButton > button span,
        .stButton > button div, .stDownloadButton > button div {
            color: inherit !important;
        }
        .stButton > button[kind="primary"] {
            background: var(--accent) !important;
            border-color: var(--accent) !important;
            color: #16130a !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: #ffe28a !important;
            color: #16130a !important;
        }

        input, textarea, [data-baseweb="select"] > div,
        [data-testid="stFileUploaderDropzone"] {
            background: var(--surface) !important;
            border-color: var(--border) !important;
            color: var(--text) !important;
            border-radius: var(--radius) !important;
        }
        input::placeholder, textarea::placeholder {
            color: #777770 !important;
            opacity: 1 !important;
        }
        input:focus, textarea:focus,
        [data-baseweb="select"] > div:focus-within {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 1px var(--accent) !important;
        }
        [data-baseweb="popover"], [data-baseweb="menu"],
        [data-baseweb="option"] {
            background: var(--surface-muted) !important;
            color: var(--text) !important;
        }
        [data-baseweb="option"]:hover {
            background: var(--accent-soft) !important;
        }
        [data-testid="stFileUploaderDropzone"] small,
        [data-testid="stFileUploaderDropzone"] span {
            color: var(--muted) !important;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
        }
        [data-testid="stAlert"] {
            background: var(--surface-muted) !important;
            border: 1px solid var(--border);
            color: var(--text) !important;
        }
        [data-testid="stAlert"] p { color: var(--text) !important; }
        [data-testid="stCodeBlock"] {
            background: var(--surface-muted) !important;
            border: 1px solid var(--border);
        }
        [data-testid="stProgressBar"] > div > div { background: var(--accent) !important; }

        .relay-mark {
            width: 30px; height: 30px; border-radius: 7px;
            background: var(--accent); color: #16130a;
            display: inline-flex; align-items: center; justify-content: center;
            font-weight: 700; margin-right: 8px;
        }
        .brand-name { font-size: 1.05rem; color: var(--text); font-weight: 600; vertical-align: middle; }
        .brand-subtitle { color: var(--muted); font-size: .72rem; margin: 4px 0 0 40px; }
        .eyebrow { color: var(--accent); font-size: .72rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
        .page-subtitle { color: var(--muted) !important; margin-top: -.65rem; margin-bottom: 1.5rem; }
        .surface, .surface-tight {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
        }
        .surface { padding: 1.1rem 1.2rem; }
        .surface-tight { padding: .8rem 1rem; }
        .section-label {
            color: var(--muted); font-size: .73rem; font-weight: 700;
            text-transform: uppercase; letter-spacing: .08em; margin-bottom: .45rem;
        }
        .status-badge {
            display: inline-flex; align-items: center; border-radius: 999px;
            padding: .25rem .55rem; font-size: .72rem; font-weight: 700; line-height: 1;
        }
        .badge-success { background: var(--success-soft); color: var(--success); }
        .badge-warning { background: var(--warning-soft); color: var(--warning); }
        .badge-danger { background: var(--danger-soft); color: var(--danger); }
        .badge-neutral { background: var(--surface-muted); color: var(--muted); }
        .auto, .review {
            margin: .8rem 0;
            padding: .85rem 1rem;
            border: 1px solid var(--border);
            border-left: 3px solid var(--success);
            border-radius: var(--radius);
            background: var(--success-soft);
            color: var(--text);
        }
        .review {
            border-left-color: var(--warning);
            background: var(--warning-soft);
        }
        .confidence-value { font-size: 1.8rem; font-weight: 600; color: var(--text); }
        .confidence-bar { height: 7px; background: var(--border); border-radius: 99px; overflow: hidden; margin: .5rem 0 .25rem; }
        .confidence-fill { height: 100%; background: var(--success); border-radius: 99px; }
        .confidence-fill.warning { background: var(--warning); }
        .metric-context { color: var(--muted); font-size: .78rem; }
        .activity-row { border-bottom: 1px solid var(--border); padding: .7rem 0; }
        .activity-row:last-child { border-bottom: 0; }
        .activity-time { color: var(--muted); font-size: .75rem; }
        .workflow { display: flex; gap: 0; margin: 1rem 0 1.5rem; overflow-x: auto; }
        .workflow-step { flex: 1; min-width: 110px; border-top: 2px solid var(--border); padding-top: .5rem; color: var(--muted); font-size: .78rem; }
        .workflow-step.active { border-color: var(--accent); color: var(--accent); font-weight: 700; }
        .empty-state { text-align: center; padding: 2.2rem 1rem; color: var(--muted); border: 1px dashed var(--border); border-radius: var(--radius); background: var(--surface); }

        @media (max-width: 720px) {
            .block-container { padding: 4rem .75rem 2rem; }
            [data-testid="stMainBlockContainer"] { padding-top: 68px !important; }
            h1 { font-size: 1.65rem !important; }
            .workflow-step { min-width: 96px; font-size: .7rem; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
