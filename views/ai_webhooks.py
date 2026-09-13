"""
AI Chatbots & AI Call Agents Webhook Integration View
"""
import streamlit as st

def render_ai_webhooks():
    """Render Webhook API documentation and live endpoint instructions."""
    st.subheader("🤖 Open Webhook Receiver & AI Agent Integration")

    st.markdown("""
    Use your open webhook endpoint to automatically ingest leads from **AI Call Agents** (Retell AI, Bland AI, Vapi) 
    and **AI Chatbots** (Voiceflow, Custom GPTs, Web forms) directly into your **`lead-snapper`** Firebase Firestore database.
    """)

    st.markdown("---")

    st.markdown("### 🌐 Live Webhook Endpoint URL")
    st.code("POST http://localhost:5001/api/v1/leads/webhook", language="http")

    st.markdown("---")

    st.markdown("### ⚡ Test Payload with `curl` (Run in Terminal)")
    st.code("""
curl -X POST http://localhost:5001/api/v1/leads/webhook \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Alex Mercer",
    "company": "Apex Technologies",
    "email": "alex@apextech.com",
    "phone": "+1 555-0199",
    "status": "Qualified",
    "priority": "High",
    "source": "AI Call Agent",
    "estimated_value": 12500,
    "notes": "Qualified by Retell AI call agent. Wants demo scheduled."
  }'
    """, language="bash")

    st.markdown("---")

    st.markdown("### 📋 Accepted JSON Fields")
    st.markdown("""
    - `name` / `full_name` *(string)*: Lead contact name
    - `company` / `company_name` *(string)*: Lead company name
    - `email` *(string)*: Email address
    - `phone` / `phone_number` *(string)*: Contact phone number
    - `status` *(string)*: Stage (`New`, `Contacted`, `Qualified`, `Proposal Sent`, `Won`, `Lost`)
    - `priority` *(string)*: `Low`, `Medium`, `High`, `Urgent`
    - `source` / `agent_name` *(string)*: Source name (e.g. `Retell AI`, `Bland AI`, `Vapi`, `Google Scraper`)
    - `estimated_value` / `deal_value` *(number)*: Estimated deal value
    - `notes` / `transcript` *(string)*: Call transcript or chatbot notes
    """)

    st.info("💡 You can run the background webhook server using: `python streamlit-crm/webhook_server.py`")
