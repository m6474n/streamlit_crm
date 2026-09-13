"""
Single Reusable Lead Form View (Create & Edit)
"""
import streamlit as st
from datetime import datetime, date
from config import STATUSES, PRIORITIES, SOURCES
from db import add_lead, update_lead, delete_lead

def render_lead_form(lead=None, on_close=None):
    """
    Single Reusable Lead Form.
    If lead is None -> Create mode.
    If lead is provided -> Edit mode.
    """
    is_edit = lead is not None
    title = f"✏️ Edit Lead: {lead.get('company', '')} ({lead.get('name', '')})" if is_edit else "➕ Add New Lead"

    st.markdown(f"#### {title}")

    form_key = f"lead_form_{lead['id'] if is_edit else 'new'}"

    with st.form(form_key, clear_on_submit=not is_edit):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Full Name *", value=lead.get("name", "") if is_edit else "", placeholder="e.g. Sarah Jenkins")
            company = st.text_input("Company Name *", value=lead.get("company", "") if is_edit else "", placeholder="e.g. Acme Corp")
            email = st.text_input("Email Address *", value=lead.get("email", "") if is_edit else "", placeholder="e.g. sarah@acme.com")
            phone = st.text_input("Phone Number", value=lead.get("phone", "") if is_edit else "", placeholder="e.g. +1 555-0199")

        with col2:
            status_val = lead.get("status", STATUSES[0]) if is_edit else STATUSES[0]
            status_idx = STATUSES.index(status_val) if status_val in STATUSES else 0
            status = st.selectbox("Pipeline Status", STATUSES, index=status_idx)

            prio_val = lead.get("priority", PRIORITIES[1]) if is_edit else PRIORITIES[1]
            prio_idx = PRIORITIES.index(prio_val) if prio_val in PRIORITIES else 0
            priority = st.selectbox("Priority Level", PRIORITIES, index=prio_idx)

            src_val = lead.get("source", SOURCES[0]) if is_edit else SOURCES[0]
            src_idx = SOURCES.index(src_val) if src_val in SOURCES else 0
            source = st.selectbox("Lead Source", SOURCES, index=src_idx)

            est_val = st.number_input("Estimated Value ($)", min_value=0, value=int(lead.get("estimated_value", 5000)) if is_edit else 5000, step=500)

        notes = st.text_area("Notes / Conversation History", value=lead.get("notes", "") if is_edit else "", placeholder="Key requirements, customer call summary...")

        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            submit_label = "💾 Update Lead" if is_edit else "🚀 Create Lead"
            submitted = st.form_submit_button(submit_label, type="primary", use_container_width=True)

        if submitted:
            if not name.strip() or not company.strip() or not email.strip():
                st.error("Full Name, Company Name, and Email Address are required!")
            else:
                lead_data = {
                    "name": name.strip(),
                    "company": company.strip(),
                    "email": email.strip().lower(),
                    "phone": phone.strip(),
                    "status": status,
                    "priority": priority,
                    "source": source,
                    "estimated_value": int(est_val),
                    "notes": notes.strip()
                }

                if is_edit:
                    update_lead(lead["id"], lead_data)
                    st.success(f"Lead {lead['id']} updated successfully!")
                else:
                    lead_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_id = add_lead(lead_data)
                    st.success(f"Lead {new_id} ({company}) created!")
                st.rerun()

    if is_edit:
        with st.expander("🗑️ Delete Lead"):
            st.write("Permanently delete this lead from CRM and Firestore?")
            if st.button(f"Confirm Delete {lead['id']}", type="primary"):
                delete_lead(lead["id"])
                st.warning(f"Lead {lead['id']} deleted.")
                st.rerun()
