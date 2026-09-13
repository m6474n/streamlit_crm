"""
Leads Directory & Inline Management View
"""
import streamlit as st
import pandas as pd
from config import STATUSES, PRIORITIES, SOURCES
from db import update_lead, delete_lead
from views.lead_form import render_lead_form

def render_leads_table(leads):
    """Render interactive searchable leads directory with inline Add/Edit form."""
    st.subheader("📋 Leads Directory")

    # Expand Add Lead Form by default if empty database or if user toggled
    expand_add = len(leads) == 0 or st.session_state.get("show_add_form", False)

    with st.expander("➕ Create New Lead", expanded=expand_add):
        render_lead_form(lead=None)

    st.markdown("---")

    if not leads:
        st.info("💡 Your leads database is currently empty. Use the form above to add your first lead or connect your AI Chatbot/Call Agent webhook!")
        return

    # Filters Section
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1, 1, 1])

    with f_col1:
        search_query = st.text_input("🔍 Search leads...", placeholder="Name, company, email...", key="lead_search_input").strip().lower()

    with f_col2:
        selected_status = st.selectbox("Filter Status", ["All"] + STATUSES)

    with f_col3:
        selected_priority = st.selectbox("Filter Priority", ["All"] + PRIORITIES)

    with f_col4:
        selected_source = st.selectbox("Filter Source", ["All"] + SOURCES)

    # Filter Logic
    filtered = leads
    if search_query:
        filtered = [
            l for l in filtered
            if search_query in l.get("name", "").lower()
            or search_query in l.get("company", "").lower()
            or search_query in l.get("email", "").lower()
        ]

    if selected_status != "All":
        filtered = [l for l in filtered if l.get("status") == selected_status]

    if selected_priority != "All":
        filtered = [l for l in filtered if l.get("priority") == selected_priority]

    if selected_source != "All":
        filtered = [l for l in filtered if l.get("source") == selected_source]

    st.markdown(f"**Showing {len(filtered)} of {len(leads)} leads**")

    # Data Table Display
    if filtered:
        table_data = []
        for l in filtered:
            table_data.append({
                "ID": l.get("id"),
                "Company": l.get("company"),
                "Contact": l.get("name"),
                "Email": l.get("email"),
                "Phone": l.get("phone", "N/A"),
                "Status": l.get("status"),
                "Priority": l.get("priority"),
                "Source": l.get("source"),
                "Value ($)": f"${l.get('estimated_value', 0):,}",
                "Created": l.get("created_at")
            })
            
        df_display = pd.DataFrame(table_data)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Inline Edit Section
        st.markdown("##### ✏️ Edit or Update Lead Details")
        lead_options = {f"{l['id']} - {l.get('company')} ({l.get('name')})": l for l in filtered}
        selected_lead_key = st.selectbox("Select Lead to Edit", list(lead_options.keys()), key="directory_edit_select")
        target_lead = lead_options[selected_lead_key]

        with st.expander(f"✏️ Edit Lead Form: {target_lead['id']} ({target_lead.get('company')})", expanded=False):
            render_lead_form(lead=target_lead)

        st.markdown("---")

        # CSV Export Button
        csv_bytes = df_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Filtered Leads (CSV)",
            data=csv_bytes,
            file_name="leads_directory_export.csv",
            mime="text/csv"
        )
    else:
        st.warning("No leads match your search filters.")
