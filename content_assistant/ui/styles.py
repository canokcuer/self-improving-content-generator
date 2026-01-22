"""Custom styles for TheLifeCo Content Assistant.

Modern, minimal UI styling using custom CSS.
"""

import base64
from pathlib import Path

# TheLifeCo brand colors
COLORS = {
    "primary": "#2D5A3D",      # Deep forest green
    "primary_light": "#4A7C5B",
    "secondary": "#8B9D83",    # Sage green
    "accent": "#C4A962",       # Warm gold
    "background": "#FAFAFA",
    "surface": "#FFFFFF",
    "text": "#1A1A1A",
    "text_secondary": "#6B7280",
    "border": "#E5E7EB",
    "success": "#059669",
    "error": "#DC2626",
}

CUSTOM_CSS = """
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global styles */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    /* Custom header */
    .app-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 0 2rem 0;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 2rem;
    }

    .app-header img {
        height: 48px;
        width: auto;
    }

    .app-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1A1A1A;
        margin: 0;
    }

    .app-header p {
        font-size: 0.875rem;
        color: #6B7280;
        margin: 0;
    }

    /* Cards */
    .card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    .card-header {
        font-size: 1.125rem;
        font-weight: 600;
        color: #1A1A1A;
        margin-bottom: 1rem;
    }

    /* Buttons */
    .stButton > button {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }

    .stButton > button[kind="primary"] {
        background: #2D5A3D;
        border: none;
        color: white;
    }

    .stButton > button[kind="primary"]:hover {
        background: #4A7C5B;
    }

    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 1px solid #E5E7EB;
        color: #1A1A1A;
    }

    .stButton > button[kind="secondary"]:hover {
        background: #F9FAFB;
        border-color: #D1D5DB;
    }

    /* Form inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        font-family: 'Inter', sans-serif;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        padding: 0.75rem;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #2D5A3D;
        box-shadow: 0 0 0 3px rgba(45, 90, 61, 0.1);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #FAFAFA;
        border-right: 1px solid #E5E7EB;
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: #1A1A1A;
    }

    [data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        color: #6B7280;
    }

    /* Progress steps */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
    }

    .step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem;
        font-weight: 500;
    }

    .step-active {
        background: #EDF7F0;
        color: #2D5A3D;
    }

    .step-completed {
        background: #D1FAE5;
        color: #059669;
    }

    .step-pending {
        background: #F3F4F6;
        color: #9CA3AF;
    }

    /* Dividers */
    hr {
        border: none;
        border-top: 1px solid #E5E7EB;
        margin: 1.5rem 0;
    }

    /* Success/Error messages */
    .stSuccess {
        background: #D1FAE5;
        color: #065F46;
        border-radius: 8px;
    }

    .stError {
        background: #FEE2E2;
        color: #991B1B;
        border-radius: 8px;
    }

    /* Login page specific */
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
    }

    .login-logo {
        text-align: center;
        margin-bottom: 2rem;
    }

    .login-logo img {
        height: 64px;
        width: auto;
        margin-bottom: 1rem;
    }

    .login-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #1A1A1A;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .login-subtitle {
        font-size: 0.875rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }

    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
    }

    .divider::before,
    .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #E5E7EB;
    }

    .divider span {
        padding: 0 1rem;
        color: #9CA3AF;
        font-size: 0.875rem;
    }

    /* Expander */
    .streamlit-expanderHeader {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #1A1A1A;
        background: #F9FAFB;
        border-radius: 8px;
    }

    /* Radio buttons in sidebar */
    .stRadio > label {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        border-radius: 8px 8px 0 0;
    }

    /* Preview content */
    .preview-box {
        background: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 1.5rem;
    }

    .preview-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #6B7280;
        margin-bottom: 0.5rem;
    }

    /* Content text area */
    .content-output {
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.75;
        color: #1A1A1A;
    }

    /* Rating stars */
    .rating-star {
        color: #C4A962;
        font-size: 1.5rem;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        padding: 2rem 0;
        color: #9CA3AF;
        font-size: 0.75rem;
    }
</style>
"""


def inject_custom_css():
    """Inject custom CSS into the Streamlit app."""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def get_logo_base64() -> str:
    """Get the logo as a base64 encoded string for HTML embedding."""
    logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


def get_logo_path() -> Path:
    """Get the path to the logo file."""
    return Path(__file__).parent.parent / "assets" / "logo.png"


def render_logo_header(logo_url: str = None, title: str = "Content Assistant", subtitle: str = None):
    """Render the app header with logo.

    Args:
        logo_url: URL or path to logo image
        title: Header title text
        subtitle: Optional subtitle text
    """
    import streamlit as st

    if logo_url:
        header_html = f'''
        <div class="app-header">
            <img src="{logo_url}" alt="Logo">
            <div>
                <h1>{title}</h1>
                {f'<p>{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        '''
    else:
        header_html = f'''
        <div class="app-header">
            <div>
                <h1>{title}</h1>
                {f'<p>{subtitle}</p>' if subtitle else ''}
            </div>
        </div>
        '''

    st.markdown(header_html, unsafe_allow_html=True)


def render_step_indicator(steps: list, current_step: str):
    """Render a modern step indicator.

    Args:
        steps: List of step names
        current_step: Name of the current step
    """
    import streamlit as st

    current_index = steps.index(current_step) if current_step in steps else 0

    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[i]:
            if i < current_index:
                st.markdown(f'''
                    <div class="step step-completed">
                        <span>✓</span> {step.title()}
                    </div>
                ''', unsafe_allow_html=True)
            elif i == current_index:
                st.markdown(f'''
                    <div class="step step-active">
                        <span>{i + 1}</span> {step.title()}
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div class="step step-pending">
                        <span>{i + 1}</span> {step.title()}
                    </div>
                ''', unsafe_allow_html=True)
