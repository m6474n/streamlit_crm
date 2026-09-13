"""
Lead Detail & Activity Follow-up Log View
"""
import streamlit as st
from db import add_lead_activity, update_lead
from utils import format_currency

def render_lead_detail(leads):
    """Render Lead Detail, Follow-up Timeline, and Activity Tracker."""
    st.subheader("📝 Lead Activity & Follow-up Timeline")

    if not leads:
        st.info("No leads available.")
        return

    lead_map = {f"{l['id']} - {l['company']} ({l['name']})": l for l in leads}
    selected_key = st.selectbox("Select Lead to Inspect", list(lead_map.keys()), key="detail_lead_select")
    lead = lead_map[selected_key]

    # Lead Header Card
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"**Contact:** {lead['name']}")
        st.markdown(f"**Company:** {lead['company']}")
    with col2:
        st.markdown(f"**Email:** {lead['email']}")
        st.markdown(f"**Phone:** {lead.get('phone', 'N/A')}")
    with col3:
        st.markdown(f"**Status:** `{lead['status']}`")
        st.markdown(f"**Priority:** `{lead['priority']}`")
    with col4:
        st.markdown(f"**Value:** `{format_currency(lead.get('estimated_value', 0))}`")
        st.markdown(f"**Source:** `{lead['source']}`")

    st.markdown("---")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("##### ➕ Log New Activity / Follow-up Note")
        with st.form("new_activity_form", clear_on_submit=True):
            author = st.selectbox("Logged By", ["AI Agent", "Sales Rep", "System Webhook", "Manager"])
            note_text = st.text_area("Note / Discussion / Call Summary", placeholder="Client confirmed demo date...")
            submit_act = st.form_submit_button("📌 Save Activity Note", use_container_width=True)

            if submit_act:
                if note_text.strip():
                    add_lead_activity(lead["id"], author, note_text.strip())
                    st.success("Activity logged!")
                    st.rerun()
                else:
                    st.error("Note content cannot be empty.")

    with col_right:
        st.markdown("##### ⏳ Activity Timeline")
        activities = lead.get("activities", [])
        if activities:
            for act in activities:
                st.markdown(
                    f"""
                    <div style='background-color: #1e293b; padding: 10px 14px; border-radius: 8px; margin-bottom: 8px; border-left: 3px solid #3b82f6;'>
                        <span style='font-size: 0.8rem; color: #94a3b8;'>{act.get('timestamp', 'N/A')} • <b>{act.get('author', 'User')}</b></span>
                        <p style='margin: 4px 0 0 0; font-size: 0.92rem; color: #f1f5f9;'>{act.get('note', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No activity history yet.")
