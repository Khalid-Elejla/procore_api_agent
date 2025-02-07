# app/interface.py
import os
import streamlit as st
from datetime import datetime
from backend.main import run_agent_graph
from app.utils.auth import authenticate, clear_auth_state
from streamlit_mic_recorder import mic_recorder

def initialize_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

def main():
    st.set_page_config(page_title="Procore AI Assistant", layout="wide")

    # Initialize session state
    initialize_session_state()

    # Add a custom title and a description
    st.title("Welcome to Procore AI Assistant")
    st.markdown("### How can I assist you today?")

    # Add a logout button in the sidebar
    with st.sidebar:
        if st.button("Logout"):
            clear_auth_state()
            st.rerun()

    # Run authentication check
    access_token = authenticate()

    # Proceed only if authenticated
    if access_token:
        try:
            # Sidebar section for file management
            with st.sidebar:
                st.subheader("📂 File Upload")
                uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt", "xls"])

                if uploaded_file is not None:
                    st.session_state.uploaded_files.append(uploaded_file)
                    st.success(f"{uploaded_file.name} uploaded successfully!")

            # Display existing chat history first
            if st.session_state.messages:
                for message in st.session_state.messages:
                    st.chat_message("user").markdown(f"**You:** {message['user']}")
                    st.chat_message("assistant").markdown(f"**Assistant:** {message['assistant']}")

            # Chat input for user messages
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                user_input = st.chat_input("Type your question here...")
            with col2:
                audio = mic_recorder(
                    start_prompt="🎤 Speak",
                    stop_prompt="⏹️ Stop",
                    format="wav",
                    key='recorder'
                )

            # Set the access token as an environment variable
            os.environ['access_token'] = access_token

            if user_input or audio:
                # Display the new user message immediately
                if user_input:
                    st.chat_message("user").markdown(f"**You:** {user_input}")
                    query = user_input
                elif audio:
                    st.chat_message("user").markdown("**You:** (Audio message)")
                    query = audio['bytes']  # Assuming the audio is sent as bytes
                    import logging
                    logging.info(type(query))
                    

                # Show thinking spinner below all messages
                with st.spinner("Thinking..."):
                    try:
                        response = run_agent_graph(query=query)
                        logging.error("response",type(response),response)

                        st.session_state.messages.append({
                            "user": query if isinstance(query, str) else "(Audio message)",
                            "assistant": response
                        })
                    except Exception as e:
                        logging.error(f"An error occurred: {str(e)}")


                # Display the new assistant response
                st.chat_message("assistant").markdown(f"**Assistant:** {response}")

                # # Play the audio response
                # play_audio(response)

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            st.error(f"An error occurred: {str(e)}")

            raise RuntimeError("Graph building failed") from e 
            clear_auth_state()
            st.rerun()



    else:
        st.warning("Please authenticate to continue.")
        st.stop()



if __name__ == "__main__":
    main()