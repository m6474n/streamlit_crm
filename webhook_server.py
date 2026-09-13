"""
Open Webhook Receiver Service for lead-snapper CRM
Receives POST requests from AI Chatbots, AI Call Agents, & Webhooks, 
and directly saves leads to Firebase Firestore.
"""
import os
import json
import random
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load local .env
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

app = Flask(__name__)

# Initialize Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, firestore

def init_firebase_admin():
    if firebase_admin._apps:
        return firestore.client()

    # 1. Try raw JSON string from env first
    raw_json = os.environ.get("FIREBASE_CREDENTIALS_JSON", "").strip()
    if raw_json:
        try:
            cred = credentials.Certificate(json.loads(raw_json))
            firebase_admin.initialize_app(cred)
            return firestore.client()
        except Exception:
            pass

    # 2. Fall back to file paths
    cred_path = os.environ.get("CRM_FIREBASE_CREDENTIALS_PATH", "").strip()
    possible_paths = []
    if cred_path:
        possible_paths.extend([Path(cred_path), Path(__file__).parent / cred_path])
    possible_paths.extend([
        Path(__file__).parent / "lead-snapper.json",
        Path("streamlit-crm/lead-snapper.json")
    ])
    
    for p in possible_paths:
        if p and p.exists() and p.is_file():
            cred = credentials.Certificate(str(p))
            firebase_admin.initialize_app(cred)
            return firestore.client()
        
    raise RuntimeError("Firebase Service Account JSON not found.")

# Pre-initialize db
db = None
try:
    db = init_firebase_admin()
except Exception as e:
    print(f"Warning: Firebase Webhook Init: {e}")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "lead-snapper webhook"}), 200

@app.route('/api/v1/leads/webhook', methods=['POST'])
def receive_lead_webhook():
    """Public Endpoint for AI Agents & Webhooks to directly create leads in Firebase."""
    global db
    if not db:
        try:
            db = init_firebase_admin()
        except Exception as e:
            return jsonify({"error": f"Firebase not configured: {str(e)}"}), 500

    data = request.get_json(silent=True) or request.form.to_dict() or {}

    name = data.get("name") or data.get("full_name") or data.get("contact_name") or "Unknown Contact"
    company = data.get("company") or data.get("company_name") or "N/A"
    email = data.get("email") or ""
    phone = data.get("phone") or data.get("phone_number") or ""
    status = data.get("status") or "New"
    priority = data.get("priority") or "High"
    source = data.get("source") or data.get("agent_name") or "AI Webhook"
    notes = data.get("notes") or data.get("transcript") or data.get("summary") or "Lead captured via Webhook API"
    est_val = int(data.get("estimated_value") or data.get("deal_value") or 5000)

    # Generate document ID
    lead_id = f"LEAD-{random.randint(10000, 99999)}"

    lead_doc = {
        "id": lead_id,
        "name": name,
        "company": company,
        "email": email.lower(),
        "phone": phone,
        "status": status,
        "priority": priority,
        "source": source,
        "estimated_value": est_val,
        "notes": notes,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "activities": [
            {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "author": source,
                "note": f"Lead ingested automatically via Open Webhook endpoint."
            }
        ]
    }

    try:
        db.collection("leads").document(lead_id).set(lead_doc)
        return jsonify({
            "status": "success",
            "message": "Lead captured and saved directly to Firebase Firestore",
            "lead_id": lead_id,
            "data": lead_doc
        }), 201
    except Exception as e:
        return jsonify({"error": f"Firestore write error: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("WEBHOOK_PORT", 5001))
    print(f"Open Webhook Server running on http://0.0.0.0:{port}/api/v1/leads/webhook")
    app.run(host='0.0.0.0', port=port, debug=False)

