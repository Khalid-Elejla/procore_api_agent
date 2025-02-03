# # pages/oauth_callback.py
# import streamlit as st
# from urllib.parse import parse_qs
# import json

# def oauth_callback():
#   st.set_page_config(page_title="Authentication Callback")
  
#   # Get the code from URL parameters
#   query_params = st.query_params
#   code = query_params.get('code', [None])[0]
  
#   if code:
#       # Store the code in session state
#       st.session_state['auth_code'] = code
#       st.success("Authentication successful! You can close this tab and return to the main application.")
      
#       # Add JavaScript to close the window after a brief delay
#       st.components.v1.html(
#           """
#           <script>
#               setTimeout(function() {
#                   window.close();
#               }, 2000);
#           </script>
#           """,
#           height=0
#       )
#   else:
#       st.error("No authentication code received.")

# if __name__ == "__main__":
#   oauth_callback()
# pages/oauth_callback.py
import streamlit as st

def oauth_callback():
  st.set_page_config(page_title="Authentication Callback")

  # Get the code from URL parameters
  query_params = st.experimental_get_query_params()
  code = query_params.get('code', [None])[0]

  if code:
      # Store the code in session state
      st.session_state['auth_code'] = code
      st.success("Authentication successful! Redirecting to the main application...")

      # Redirect to the main app page after a short delay
      st.components.v1.html(
          """
          <script>
              setTimeout(function() {
                  window.location.replace('/');
              }, 2000);
          </script>
          """,
          height=0,
      )
  else:
      st.error("No authentication code received.")

if __name__ == "__main__":
  oauth_callback()