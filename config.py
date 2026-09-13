import os
from pathlib import Path
from dotenv import load_dotenv

# Load local .env inside streamlit-crm
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

APP_TITLE = "lead-snapper CRM"
APP_ICON = "⚡"



# Pipeline Stages
STATUSES = [
    "New",
    "Contacted",
    "Qualified",
    "Proposal Sent",
    "Won",
    "Lost"
]

STATUS_COLORS = {
    "New": "#3B82F6",          # Blue
    "Contacted": "#8B5CF6",    # Purple
    "Qualified": "#F59E0B",    # Amber
    "Proposal Sent": "#06B6D4",# Cyan
    "Won": "#10B981",          # Green
    "Lost": "#EF4444"          # Red
}

PRIORITIES = ["Low", "Medium", "High", "Urgent"]

PRIORITY_COLORS = {
    "Low": "#6B7280",
    "Medium": "#3B82F6",
    "High": "#F59E0B",
    "Urgent": "#EF4444"
}

SOURCES = [
    "AI Chatbot",
    "AI Call Agent",
    "Google Scraper",
    "Website Form",
    "LinkedIn Outbound",
    "Manual Input",
    "API Webhook"
]

CUSTOM_CSS = """
<style>
    /* Sleek Dark Theme Customization */
    .stApp {
        background-color: #0e1726;
        color: #e0e6ed;
    }
    .metric-card {
        background: linear-gradient(135deg, #1b2e4b 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        color: white;
    }
    /* Hide Sidebar Scrollbar */
    [data-testid="stSidebarUserContent"], [data-testid="stSidebarContent"], section[data-testid="stSidebar"] {
        overflow: hidden !important;
    }
</style>

"""
