"""
Deversol Streamlit Lead CRM Dashboard
Main Application Entry point
"""
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="lead-snapper CRM",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import APP_TITLE, APP_ICON, CUSTOM_CSS
from db import init_db_session, get_all_leads
from views.analytics import render_analytics
from views.leads_table import render_leads_table
from views.lead_detail import render_lead_detail
from views.ai_webhooks import render_ai_webhooks
from views.auth import render_auth_page, decode_session

# Inject Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize Session & Auth
init_db_session()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Auto-restore session from URL query params
if not st.session_state.authenticated:
    session_token = st.query_params.get("session")
    if session_token:
        sess = decode_session(session_token)
        if sess and sess.get("email"):
            st.session_state.authenticated = True
            st.session_state.user_email = sess.get("email")
            st.session_state.user_uid = sess.get("uid")

if not st.session_state.authenticated:
    render_auth_page()
else:
    leads = get_all_leads()

    # Professional Sidebar Navigation Layout
    with st.sidebar:
        st.markdown(f"### {APP_ICON} {APP_TITLE}")
        
        user_email = st.session_state.get('user_email', 'Admin User')
        st.markdown(
            f"""
            <div style='background-color: #1e293b; padding: 10px 12px; border-radius: 8px; border-left: 3px solid #3b82f6; margin-bottom: 15px;'>
                <div style='font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;'>Logged in as</div>
                <div style='font-size: 0.9rem; color: #f8fafc; font-weight: 600; text-overflow: ellipsis; overflow: hidden;'>{user_email}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        menu = st.radio(
            "Main Menu",
            [
                "📊 Analytics Dashboard",
                "📋 Leads Directory",
                "📝 Activity & Follow-ups",
                "🤖 AI Webhooks Setup"
            ]
        )

        st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.user_uid = None
            if "session" in st.query_params:
                del st.query_params["session"]
            st.rerun()


    # View Router
    if menu == "📊 Analytics Dashboard":
        render_analytics(leads)
    elif menu == "📋 Leads Directory":
        render_leads_table(leads)
    elif menu == "📝 Activity & Follow-ups":
        render_lead_detail(leads)
    elif menu == "🤖 AI Webhooks Setup":
        render_ai_webhooks()
