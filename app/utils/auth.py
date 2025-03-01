import os
import requests
import streamlit as st
from datetime import datetime, timedelta
import logging

# Procore credentials
PROCORE_CLIENT_ID = os.getenv("PROCORE_CLIENT_ID")
PROCORE_CLIENT_SECRET = os.getenv("PROCORE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("LOCAL_REDIRECT_URI")
AUTHORIZATION_URL = os.getenv("AUTHORIZATION_URL")
TOKEN_URL = os.getenv("TOKEN_URL")

def clear_auth_state():
  """Clear all authentication related session state"""
  if 'access_token' in st.session_state:
      del st.session_state['access_token']
  if 'refresh_token' in st.session_state:
      del st.session_state['refresh_token']
  if 'token_expires_at' in st.session_state:
      del st.session_state['token_expires_at']
  # Clear query parameters
  st.query_params.clear()

def refresh_token():
  """Attempt to refresh the access token"""
  if 'refresh_token' not in st.session_state:
      return False

  refresh_data = {
      'grant_type': 'refresh_token',
      'refresh_token': st.session_state['refresh_token'],
      'client_id': PROCORE_CLIENT_ID,
      'client_secret': PROCORE_CLIENT_SECRET
  }

  try:
      response = requests.post(
          TOKEN_URL,
          data=refresh_data,
          headers={'Content-Type': 'application/x-www-form-urlencoded'}
      )

      if response.status_code == 200:
          token_info = response.json()
          st.session_state["access_token"] = token_info["access_token"]
          st.session_state["refresh_token"] = token_info.get("refresh_token", st.session_state["refresh_token"])
          st.session_state["token_expires_at"] = datetime.now() + timedelta(seconds=token_info["expires_in"])
          return True
      else:
          clear_auth_state()
          return False

  except Exception as e:
      st.error(f"Token refresh error: {str(e)}")
      clear_auth_state()
      return False

def authenticate():

  """Main authentication function"""
  # Check if we have a valid token
  if (
      "access_token" in st.session_state
      and "token_expires_at" in st.session_state
  ):
      # If token is about to expire in the next 5 minutes, try to refresh it
      if datetime.now() + timedelta(minutes=5) >= st.session_state["token_expires_at"]:
          if refresh_token():
              return st.session_state["access_token"]
      # If token is still valid, use it
      elif st.session_state["token_expires_at"] > datetime.now():
          return st.session_state["access_token"]

  # Create the authorization URL
  auth_url = f"{AUTHORIZATION_URL}?client_id={PROCORE_CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
#   logging.error(f"REDIRECT_URI")
#   logging.error(f"auth_url")

  # Check if code is in query params
  query_params = st.query_params
  code = query_params.get('code')

  if code:
      # Exchange code for access token
      token_data = {
          'grant_type': 'authorization_code',
          'code': code,
          'client_id': PROCORE_CLIENT_ID,
          'client_secret': PROCORE_CLIENT_SECRET,
          'redirect_uri': REDIRECT_URI
      }

      try:
          with st.spinner("Authenticating..."):
              response = requests.post(
                  TOKEN_URL, 
                  data=token_data,
                  headers={'Content-Type': 'application/x-www-form-urlencoded'}
              )
              
              if response.status_code == 200:
                  token_info = response.json()
                  st.session_state["access_token"] = token_info["access_token"]
                  st.session_state["refresh_token"] = token_info.get("refresh_token")
                  st.session_state["token_expires_at"] = datetime.now() + timedelta(seconds=token_info["expires_in"])
                  # Clear the code from URL
                  st.query_params.clear()
                  st.success("Successfully authenticated!")
                  st.rerun()
                  return st.session_state["access_token"]
              else:
                  st.error(f"Authentication failed: {response.status_code}")
                  st.json(response.json())
                  clear_auth_state()
                  return None
                  
      except Exception as e:
          st.error(f"Authentication error: {str(e)}")
          clear_auth_state()
          return None
  else:
      st.warning("Please authenticate to continue.")
      st.markdown(f"[Click here to authorize the application]({auth_url})", unsafe_allow_html=True)
      st.stop()

  return None