# app/ui/display.py
import streamlit as st
from typing import Optional

class ChatDisplay:
    @staticmethod
    def display_chat_history() -> None:
        """Display all messages in the chat history"""
        if st.session_state.messages:
            for message in st.session_state.messages:
                st.chat_message("user").markdown(f"**You:** {message['user']}")
                st.chat_message("assistant").markdown(
                    f"**Assistant:** {message['assistant']}"
                )

    @staticmethod
    def display_response(response: str,
                        error: Optional[str] = None) -> None:
        """
        Display the assistant's response or error message

        Args:
            response: The assistant's response text
            error: Optional error message to display
        """
        if error:
            st.error(f"Error: {error}")
        else:
            st.chat_message("assistant").markdown(f"**Assistant:** {response}")