# app/utils/state_manager.py
import streamlit as st
from typing import List, Dict, Any

class StateManager:
    @staticmethod
    def get_chat_history() -> List[Dict[str, Any]]:
        """Retrieve chat history from session state"""
        return st.session_state.messages

    @staticmethod
    def get_uploaded_files() -> List[Any]:
        """Retrieve uploaded files from session state"""
        return st.session_state.uploaded_files