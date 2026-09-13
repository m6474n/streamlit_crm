"""
Streamlit Lead CRM Utility Helpers
"""
import random
from datetime import datetime, timedelta

def get_initial_mock_leads():
    """Return empty list for real production leads storage."""
    return []


def format_currency(val):
    """Format numbers into clean currency strings."""
    try:
        return f"${val:,.0f}"
    except (ValueError, TypeError):
        return "$0"
