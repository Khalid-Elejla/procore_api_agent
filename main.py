import os
import streamlit as st
from datetime import datetime
from backend.main import run_agent_graph
from app.utils.auth import authenticate, clear_auth_state

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
          user_input = st.chat_input("Type your question here...")

          # Set the access token as an environment variable
          os.environ['access_token'] = access_token

          if user_input:
              # Display the new user message immediately
              st.chat_message("user").markdown(f"**You:** {user_input}")
              
              # Show thinking spinner below all messages
              with st.spinner("Thinking..."):
                  response = run_agent_graph(query=user_input)
                  st.session_state.messages.append({
                      "user": user_input,
                      "assistant": response.content
                  })
              
              # Display the new assistant response
              st.chat_message("assistant").markdown(f"**Assistant:** {response.content}")

      except Exception as e:
          st.error(f"An error occurred: {str(e)}")
          clear_auth_state()
          st.rerun()

  else:
      st.warning("Please authenticate to continue.")
      st.stop()

if __name__ == "__main__":
  main()

# import os
# import streamlit as st
# from datetime import datetime
# from backend.main import run_agent_graph
# from app.utils.auth import authenticate, clear_auth_state

# def initialize_session_state():
#   """Initialize session state variables"""
#   if "messages" not in st.session_state:
#       st.session_state.messages = []
#   if "uploaded_files" not in st.session_state:
#       st.session_state.uploaded_files = []
#   if "access_token" not in st.session_state:
#       st.session_state.access_token = None  # Initialize access token

# def main():
#   st.set_page_config(page_title="Procore AI Assistant", layout="wide")

#   # Initialize session state
#   initialize_session_state()

#   # Add a custom title and a description
#   st.title("Welcome to Procore AI Assistant")
#   st.markdown("### How can I assist you today?")

#   # Add a logout button in the sidebar
#   with st.sidebar:
#       if st.button("Logout"): AXXXXAzzzzzzzzzzzzzzzzZZZZZZ
#           clear_auth_state()
#           st.session_state.access_token = None  # Clear the access token
#           st.session_state.messages = []  # Optionally clear messages on logout
#           st.rerun()

#   # Check if the user is already authenticated
#   if st.session_state.access_token is None:
#       # Run authentication check
#       st.session_state.access_token = authenticate()

#   # Proceed only if authenticated
#   if st.session_state.access_token:
#       try:
#           # Sidebar section for file management
#           with st.sidebar:
#               st.subheader("📂 File Upload")
#               uploaded_file = st.file_uploader("Upload your document", type=["pdf", "docx", "txt", "xls"])

#               if uploaded_file is not None:
#                   st.session_state.uploaded_files.append(uploaded_file)
#                   st.success(f"{uploaded_file.name} uploaded successfully!")

#           # Display existing chat history first
#           if st.session_state.messages:
#               for message in st.session_state.messages:
#                   st.chat_message("user").markdown(f"**You:** {message['user']}")
#                   st.chat_message("assistant").markdown(f"**Assistant:** {message['assistant']}")

#           # Chat input for user messages
#           user_input = st.chat_input("Type your question here...")

#           # Set the access token as an environment variable
#           os.environ['access_token'] = st.session_state.access_token

#           if user_input:
#               # Display the new user message immediately
#               st.chat_message("user").markdown(f"**You:** {user_input}")
              
#               # Show thinking spinner below all messages
#               with st.spinner("Thinking..."):
#                   response = run_agent_graph(query=user_input)
#                   st.session_state.messages.append({
#                       "user": user_input,
#                       "assistant": response.content
#                   })
              
#               # Display the new assistant response
#               st.chat_message("assistant").markdown(f"**Assistant:** {response.content}")

#       except Exception as e:
#           st.error(f"An error occurred: {str(e)}")
#           clear_auth_state()
#           st.session_state.access_token = None  # Clear the access token on error
#           st.rerun()

#   else:
#       st.warning("Please authenticate to continue.")
#       st.stop()

# if __name__ == "__main__":
#   main()