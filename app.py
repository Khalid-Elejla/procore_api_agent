# # app/interface.py
# import os
# import logging
# import streamlit as st
# from datetime import datetime
# from backend.main import run_agent_graph
# from app.utils.auth import authenticate, clear_auth_state
# from streamlit_mic_recorder import mic_recorder

# def initialize_session_state():
#     """Initialize session state variables"""
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     if "uploaded_files" not in st.session_state:
#         st.session_state.uploaded_files = []

# def main():
#     st.set_page_config(page_title="Procore AI Assistant", layout="wide")

#     # Initialize session state
#     initialize_session_state()

#     # Add a custom title and a description
#     st.title("Welcome to Procore AI Assistant")
#     st.markdown("### How can I assist you today?")

#     # Add a logout button in the sidebar
#     with st.sidebar:
#         if st.button("Logout"):
#             clear_auth_state()
#             st.rerun()

#     # Run authentication check
#     access_token = authenticate()

#     # Proceed only if authenticated
#     if access_token:
#         try:
#             # Sidebar section for file management
#             with st.sidebar:
#                 st.subheader("📂 File Upload")
#                 uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt", "xls"])

#                 if uploaded_file is not None:
#                     st.session_state.uploaded_files.append(uploaded_file)
#                     st.success(f"{uploaded_file.name} uploaded successfully!")

#             # Display existing chat history first
#             if st.session_state.messages:
#                 for message in st.session_state.messages:
#                     st.chat_message("user").markdown(f"**You:** {message['user']}")
#                     st.chat_message("assistant").markdown(f"**Assistant:** {message['assistant']}")

#             # Chat input for user messages
#             col1, col2 = st.columns([0.85, 0.15])
#             with col1:
#                 text_query = st.chat_input("Type your question here...")
#             with col2:
#                 voice_query = mic_recorder(
#                     start_prompt="🎤 Speak",
#                     stop_prompt="⏹️ Stop",
#                     format="wav",
#                     key='recorder'
#                 )

#             # Set the access token as an environment variable
#             os.environ['access_token'] = access_token

#             if text_query or voice_query:
#                 # Determine query type and prepare components
#                 if text_query:
#                     query = text_query
#                     query_type = "text"
#                     user_message = f"**You:** {text_query}"
#                 else:  # voice_query exists
#                     query = voice_query['bytes']
#                     query_type = "voice"
#                     user_message = "**You:** (Audio message)"

#                 # Display user message immediately
#                 st.chat_message("user").markdown(user_message)

#                 # Process query
#                 with st.spinner("Thinking..."):
#                     try:
#                         response = run_agent_graph(query, query_type)
#                         logging.info(f"Response type: {type(response)}, content: {response}")

#                         # Update session state
#                         st.session_state.messages.append({
#                             "user": text_query or "(Audio message)",
#                             "assistant": response
#                         })

#                         # Display assistant response
#                         st.chat_message("assistant").markdown(f"**Assistant:** {response}")
#                     except Exception as e:
#                         logging.error(f"An error occurred: {str(e)}", exc_info=True)
#                         st.error(f"An error occurred: {str(e)}")
#                         raise RuntimeError("Graph building failed") from e
#         except RuntimeError:
#             clear_auth_state()
#             st.rerun()

#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}", exc_info=True)
#             st.error(f"An unexpected error occurred: {str(e)}")
#             clear_auth_state()
#             st.rerun()

#     else:
#         st.warning("Please authenticate to continue.")
#         st.stop()



# if __name__ == "__main__":
#     main()
#================================================================================================================
# app/interface.py
# import os
# import logging
# import streamlit as st
# from datetime import datetime
# from backend.main import run_agent_graph
# from app.utils.auth import authenticate, clear_auth_state
# from streamlit_mic_recorder import mic_recorder

# def initialize_session_state():
#     """Initialize session state variables"""
#     if "messages" not in st.session_state:
#         st.session_state.messages = []
#     if "uploaded_files" not in st.session_state:
#         st.session_state.uploaded_files = []

# def main():
#     st.set_page_config(page_title="Procore AI Assistant", layout="wide")

#     # Initialize session state
#     initialize_session_state()

#     # Add a custom title and a description
#     st.title("Welcome to Procore AI Assistant")
#     st.markdown("### How can I assist you today?")

#     # Add a logout button in the sidebar
#     with st.sidebar:
#         if st.button("Logout"):
#             clear_auth_state()
#             st.rerun()

#     # Run authentication check
#     access_token = authenticate()

#     # Proceed only if authenticated
#     if access_token:
#         try:
#             # Sidebar section for file management
#             with st.sidebar:
#                 st.subheader("📂 File Upload")
#                 uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt", "xls"])

#                 if uploaded_file is not None:
#                     st.session_state.uploaded_files.append(uploaded_file)
#                     st.success(f"{uploaded_file.name} uploaded successfully!")

#             # Chat container for message history
#             chat_container = st.container()
#             with chat_container:
#                 # Display existing chat history
#                 if st.session_state.messages:
#                     for message in st.session_state.messages:
#                         st.chat_message("user").markdown(message['user'])
#                         st.chat_message("assistant").markdown(message['assistant'])

#             # Input container at bottom
#             input_container = st.container()
#             with input_container:
#                 col1, col2 = st.columns([0.9, 0.1])
#                 with col1:
#                     text_query = st.chat_input("Type your question here...")
#                 with col2:
#                     voice_query = mic_recorder(
#                         start_prompt="🎤",
#                         stop_prompt="⏹️",
#                         format="wav",
#                         key='recorder'
#                     )

#             # Set the access token as an environment variable
#             os.environ['access_token'] = access_token

#             if text_query or voice_query:
#                 # Determine query type and prepare components
#                 if text_query:
#                     query = text_query
#                     query_type = "text"
#                     display_user = text_query
#                 else:  # voice_query exists
#                     query = voice_query['bytes']
#                     query_type = "voice"
#                     display_user = "(Audio message)"

#                 # Display user message immediately
#                 st.chat_message("user").markdown(display_user)

#                 # Process query
#                 with st.spinner("Thinking..."):
#                     try:
#                         response = run_agent_graph(query, query_type)
#                         logging.info(f"Response type: {type(response)}, content: {response}")

#                         # Update session state
#                         st.session_state.messages.append({
#                             "user": display_user,
#                             "assistant": response
#                         })

#                         # Display assistant response
#                         st.chat_message("assistant").markdown(response)
#                     except Exception as e:
#                         logging.error(f"An error occurred: {str(e)}", exc_info=True)
#                         st.error(f"An error occurred: {str(e)}")
#                         raise RuntimeError("Graph building failed") from e
#         except RuntimeError:
#             clear_auth_state()
#             st.rerun()

#         except Exception as e:
#             logging.error(f"Unexpected error: {str(e)}", exc_info=True)
#             st.error(f"An unexpected error occurred: {str(e)}")
#             clear_auth_state()
#             st.rerun()

#     else:
#         st.warning("Please authenticate to continue.")
#         st.stop()

# if __name__ == "__main__":
#     main()
#=========================================================================================================================
import os
import logging
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
    if "processing_voice" not in st.session_state:
        st.session_state.processing_voice = False
    if "last_voice_processed" not in st.session_state:
        st.session_state.last_voice_processed = 0
    if "last_voice_hash" not in st.session_state:
        st.session_state.last_voice_hash = None

def is_new_voice_input(voice_data):
    """Check if this is a new voice input"""
    if voice_data and voice_data.get('bytes'):
        current_hash = hash(str(voice_data['bytes']))
        if current_hash != st.session_state.last_voice_hash:
            st.session_state.last_voice_hash = current_hash
            return True
    return False

def process_voice_input(voice_data):
    """Process voice input with debounce and state management"""
    if not st.session_state.processing_voice:
        current_timestamp = datetime.now().timestamp()
        if current_timestamp - st.session_state.last_voice_processed > 1:  # 1-second cooldown
            st.session_state.processing_voice = True
            st.session_state.last_voice_processed = current_timestamp
            return True
    return False

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

            # Main chat container
            chat_container = st.container()
            with chat_container:
                # Display chat messages from history
                for message in st.session_state.messages:
                    if message["type"] == "user":
                        st.chat_message("user").markdown(message["content"])
                    else:
                        st.chat_message("assistant").markdown(message["content"])

            # Input area (always at bottom)
            input_col1, input_col2 = st.columns([0.9, 0.1])
            with input_col1:
                text_query = st.chat_input("Type your question here...")
            with input_col2:
                voice_query = mic_recorder(
                    start_prompt="🎤",
                    stop_prompt="⏹️",
                    format="wav",
                    key='recorder'
                )

            # Set the access token as an environment variable
            os.environ['access_token'] = access_token

            # Handle input (text or voice)
            if text_query or (voice_query and is_new_voice_input(voice_query)):
                try:
                    if text_query:
                        user_content = text_query
                        query_type = "text"
                        query = text_query
                    else:  # voice query
                        if process_voice_input(voice_query):
                            user_content = "(Audio message)"
                            query_type = "voice"
                            query = voice_query['bytes']
                        else:
                            st.rerun()
                            return

                    # Add user message to history
                    st.session_state.messages.append({
                        "type": "user", 
                        "content": user_content
                    })

                    # Process query
                    with st.spinner("Thinking..."):
                        try:
                            # Get assistant response
                            response = run_agent_graph(query, query_type)
                            
                            # Add assistant response to history
                            st.session_state.messages.append({
                                "type": "assistant",
                                "content": response
                            })

                        except Exception as e:
                            logging.error(f"An error occurred during query processing: {str(e)}", exc_info=True)
                            st.error("Sorry, I encountered an error processing your request. Please try again.")
                            
                        finally:
                            # Reset voice processing state
                            if query_type == "voice":
                                st.session_state.processing_voice = False

                    # Trigger rerun to update chat display
                    st.rerun()

                except Exception as e:
                    logging.error(f"An error occurred in input handling: {str(e)}", exc_info=True)
                    st.error("Sorry, something went wrong. Please try again.")
                    if query_type == "voice":
                        st.session_state.processing_voice = False

        except RuntimeError as e:
            logging.error(f"Runtime error occurred: {str(e)}", exc_info=True)
            clear_auth_state()
            st.rerun()

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}", exc_info=True)
            st.error("An unexpected error occurred. Please try logging in again.")
            clear_auth_state()
            st.rerun()

    else:
        st.warning("Please authenticate to continue.")
        st.stop()

if __name__ == "__main__":
    main()