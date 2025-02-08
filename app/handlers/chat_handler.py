# app/handlers/chat_handler.py
from typing import Any, Union
import streamlit as st
from datetime import datetime

class ChatHandler:
    @staticmethod
    def update_chat_history(query: Union[str, bytes],
                          response: str,
                          query_type: str = "text") -> None:
        """
        Update the chat history in session state

        Args:
            query: User's input (text or audio)
            response: Assistant's response
            query_type: Type of query ("text" or "audio")
        """
        query_display = query if query_type == "text" else "(Audio message)"

        st.session_state.messages.append({
            "user": query_display,
            "assistant": response,
            "timestamp": datetime.now().isoformat()
        })