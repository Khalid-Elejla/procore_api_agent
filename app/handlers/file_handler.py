# app/handlers/file_handler.py
from typing import BinaryIO
import streamlit as st
import logging

class FileHandler:
    @staticmethod
    def handle_file_upload(uploaded_file: BinaryIO) -> bool:
        """
        Handle file upload and storage in session state

        Args:
            uploaded_file: The uploaded file object from Streamlit

        Returns:
            bool: True if file was handled successfully, False otherwise
        """
        try:
            if uploaded_file is not None:
                # Add file to session state
                if uploaded_file.name not in [f.name for f in st.session_state.uploaded_files]:
                    st.session_state.uploaded_files.append(uploaded_file)
                    st.success(f"{uploaded_file.name} uploaded successfully!")
                    return True
                else:
                    st.warning(f"File {uploaded_file.name} already exists!")
                    return False
        except Exception as e:
            logging.error(f"Error handling file upload: {str(e)}")
            st.error("Failed to process uploaded file")
            return False