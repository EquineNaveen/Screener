import streamlit as st

def require_login():
    if not st.session_state.get("authenticated"):
        st.error("Access denied. Please log in.")
        st.stop()