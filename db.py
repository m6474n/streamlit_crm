"""
Database Service Layer for Streamlit Lead CRM
Supports Session State storage and optional live Firebase Firestore sync.
"""
import streamlit as st
import json
from utils import get_initial_mock_leads

# Optional Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

import os
from pathlib import Path

def auto_connect_firebase():
    """Attempt automatic connection to custom CRM Firebase service account file or env."""
    if not FIREBASE_AVAILABLE or st.session_state.get("firebase_connected"):
        return

    # 1. Check Streamlit Secrets (st.secrets) for Cloud Deployment
    try:
        if hasattr(st, "secrets"):
            if "FIREBASE_CREDENTIALS_JSON" in st.secrets:
                raw_json = st.secrets["FIREBASE_CREDENTIALS_JSON"]
                if isinstance(raw_json, str):
                    cred_dict = json.loads(raw_json)
                elif isinstance(raw_json, dict):
                    cred_dict = dict(raw_json)
                else:
                    cred_dict = None
                if cred_dict:
                    success, msg = connect_firebase_credentials(cred_dict)
                    if success:
                        fetch_leads_from_firestore()
                        return
            elif "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                success, msg = connect_firebase_credentials(cred_dict)
                if success:
                    fetch_leads_from_firestore()
                    return
    except Exception:
        pass

    # 2. Check raw JSON string in env
    raw_json = os.environ.get("FIREBASE_CREDENTIALS_JSON", "").strip()
    if raw_json:
        try:
            cred_dict = json.loads(raw_json)
            success, msg = connect_firebase_credentials(cred_dict)
            if success:
                fetch_leads_from_firestore()
                return
        except Exception:
            pass

    # Check file paths
    env_path = os.environ.get("CRM_FIREBASE_CREDENTIALS_PATH", "").strip()
    possible_paths = []
    if env_path:
        possible_paths.append(Path(env_path))
        possible_paths.append(Path(__file__).parent / env_path)
    possible_paths.extend([
        Path("streamlit-crm/lead-snapper.json"),
        Path(__file__).parent / "lead-snapper.json",
        Path("crm-firebase-admin.json"),
        Path(__file__).parent / "crm-firebase-admin.json"
    ])

    
    for p in possible_paths:
        if p and p.exists() and p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    cred_dict = json.load(f)
                    success, msg = connect_firebase_credentials(cred_dict)
                    if success:
                        fetch_leads_from_firestore()
                        return
            except Exception:
                pass


def fetch_leads_from_firestore():
    """Load all leads directly from active Firestore collection."""
    if not st.session_state.get("firebase_connected"):
        return
    try:
        db = firestore.client()
        docs = db.collection("leads").stream()
        remote_leads = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            remote_leads.append(d)
            
        if remote_leads:
            st.session_state.leads = remote_leads
    except Exception as e:
        st.error(f"Error fetching leads from Firestore: {e}")

def init_db_session():
    """Ensure leads database is initialized in session state."""
    if "leads" not in st.session_state:
        st.session_state.leads = get_initial_mock_leads()
    if "firebase_connected" not in st.session_state:
        st.session_state.firebase_connected = False
    if "firebase_project_id" not in st.session_state:
        st.session_state.firebase_project_id = None
    api_key = ""
    try:
        if hasattr(st, "secrets") and "FIREBASE_API_KEY" in st.secrets:
            api_key = str(st.secrets["FIREBASE_API_KEY"]).strip()
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("FIREBASE_API_KEY", "").strip()
    st.session_state.firebase_api_key = api_key
        
    # Auto connect to default project Firebase if available
    if not st.session_state.firebase_connected:
        auto_connect_firebase()



def get_all_leads():
    """Retrieve all leads from active store."""
    init_db_session()
    return st.session_state.leads

def add_lead(lead_data):
    """Add a new lead to active store."""
    init_db_session()
    new_id = f"LEAD-{1000 + len(st.session_state.leads) + 1}"
    lead_data["id"] = new_id
    if "activities" not in lead_data:
        lead_data["activities"] = [{
            "timestamp": lead_data.get("created_at"),
            "author": "Dashboard User",
            "note": "Lead created manually."
        }]
    st.session_state.leads.insert(0, lead_data)
    
    # Sync with Firestore if active
    if st.session_state.get("firebase_connected"):
        try:
            db = firestore.client()
            db.collection("leads").document(new_id).set(lead_data)
        except Exception as e:
            st.error(f"Firestore Sync Error: {e}")
            
    return new_id

def update_lead(lead_id, updated_fields):
    """Update fields on an existing lead."""
    init_db_session()
    for lead in st.session_state.leads:
        if lead["id"] == lead_id:
            lead.update(updated_fields)
            break
            
    if st.session_state.get("firebase_connected"):
        try:
            db = firestore.client()
            db.collection("leads").document(lead_id).update(updated_fields)
        except Exception as e:
            st.error(f"Firestore Update Error: {e}")

def delete_lead(lead_id):
    """Remove a lead from active store."""
    init_db_session()
    st.session_state.leads = [l for l in st.session_state.leads if l["id"] != lead_id]
    
    if st.session_state.get("firebase_connected"):
        try:
            db = firestore.client()
            db.collection("leads").document(lead_id).delete()
        except Exception as e:
            st.error(f"Firestore Delete Error: {e}")

def add_lead_activity(lead_id, author, note_text):
    """Add a note or log activity to a lead."""
    init_db_session()
    from datetime import datetime
    new_activity = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "author": author,
        "note": note_text
    }
    for lead in st.session_state.leads:
        if lead["id"] == lead_id:
            if "activities" not in lead:
                lead["activities"] = []
            lead["activities"].insert(0, new_activity)
            
            if st.session_state.get("firebase_connected"):
                try:
                    db = firestore.client()
                    db.collection("leads").document(lead_id).update({"activities": lead["activities"]})
                except Exception as e:
                    st.error(f"Firestore Activity Log Sync Error: {e}")
            break

def connect_firebase_credentials(json_dict):
    """Initialize Firebase Admin SDK with uploaded Service Account JSON."""
    if not FIREBASE_AVAILABLE:
        return False, "firebase-admin Python package is not installed."
        
    try:
        cred = credentials.Certificate(json_dict)
        project_id = json_dict.get("project_id", "custom-firebase")
        
        # Clean up existing app if re-connecting
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
            
        firebase_admin.initialize_app(cred)
        st.session_state.firebase_connected = True
        st.session_state.firebase_project_id = project_id
        return True, f"Successfully connected to Firebase Project: {project_id}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

