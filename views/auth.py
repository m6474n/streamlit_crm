"""
Firebase Authentication View (Login & Signup) for Lead-Snapper CRM
"""
import streamlit as st
import urllib.request
import json
import base64
from config import APP_TITLE, APP_ICON

def encode_session(email, uid):
    """Encode session data into url safe token for persistent login."""
    payload = json.dumps({"email": email, "uid": uid})
    return base64.urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8')

def decode_session(token_str):
    """Decode session token from URL query params."""
    try:
        decoded = base64.urlsafe_b64decode(token_str.encode('utf-8')).decode('utf-8')
        return json.loads(decoded)
    except Exception:
        return None

def firebase_auth_request(endpoint, email, password, api_key):
    """Call Firebase Auth REST API for sign in or sign up."""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return True, res_data
    except urllib.error.HTTPError as e:
        error_res = json.loads(e.read().decode('utf-8'))
        error_msg = error_res.get('error', {}).get('message', 'Authentication failed')
        return False, error_msg
    except Exception as e:
        return False, str(e)

def render_auth_page():
    """Render Login & Signup Screen for lead-snapper CRM."""
    st.markdown(f"<h1 style='text-align: center;'>{APP_ICON} lead-snapper CRM</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Secure Lead Management System</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

        with tab_login:
            st.subheader("Welcome Back")
            login_email = st.text_input("Email Address", key="login_email")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Log In", type="primary", use_container_width=True):
                if not login_email or not login_pass:
                    st.error("Please enter email and password.")
                elif not st.session_state.get("firebase_api_key"):
                    st.error("Authentication configuration error: FIREBASE_API_KEY missing in environment.")
                else:
                    success, res = firebase_auth_request("signInWithPassword", login_email.strip(), login_pass, st.session_state.firebase_api_key)
                    if success:
                        email = res.get("email", login_email)
                        uid = res.get("localId", "")
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_uid = uid
                        
                        # Save persistent browser session token
                        st.query_params["session"] = encode_session(email, uid)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(f"Login Failed: {res}")

        with tab_signup:
            st.subheader("Create Account")
            signup_email = st.text_input("Email Address", key="signup_email")
            signup_pass = st.text_input("Password", type="password", key="signup_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")

            if st.button("Sign Up", type="primary", use_container_width=True):
                if not signup_email or not signup_pass:
                    st.error("Email and password are required.")
                elif signup_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif len(signup_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif not st.session_state.get("firebase_api_key"):
                    st.error("Authentication configuration error: FIREBASE_API_KEY missing in environment.")
                else:
                    success, res = firebase_auth_request("signUp", signup_email.strip(), signup_pass, st.session_state.firebase_api_key)
                    if success:
                        email = res.get("email", signup_email)
                        uid = res.get("localId", "")
                        st.session_state.authenticated = True
                        st.session_state.user_email = email
                        st.session_state.user_uid = uid
                        
                        # Save persistent browser session token
                        st.query_params["session"] = encode_session(email, uid)
                        st.success("Account created successfully!")
                        st.rerun()
                    else:
                        st.error(f"Signup Failed: {res}")
