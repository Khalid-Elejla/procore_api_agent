import requests
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool
import os

@tool
def create_user(
    first_name: str,
    last_name: str,
    email: str,
    job_title: str
) -> Optional[Dict[str, Any]]:
    """
    Creates a new user in Procore with the given details.

    Parameters:
        first_name (str): The first name of the user
        last_name (str): The last name of the user
        email (str): The email address of the user
        job_title (str): : The job title of the user

    Returns:
        Optional[Dict[str, Any]]: The created user data if successful, None otherwise
    """

    company_id = os.getenv('PROCORE_COMPANY_ID')
    access_token = os.getenv('access_token') 

    # users_url = "https://sandbox.procore.com/rest/v1.0/users"
    users_url = "https://sandbox.procore.com/rest/v1.3/companies/{company_id}/users"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email_address": email,   
        "company_id": company_id,
        "job_title": job_title,
    }
    params = {"company_id": company_id}

    # Make the POST request
    response = requests.post(users_url, headers=headers, json=payload, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 201:
        user = response.json()
        print("User created successfully:")
        return {"status": "created", "user": user}
    else:
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Body: {response.text}")
        return {"status": response.status_code, "message": response.text}
    
    # elif response.status_code == 404:
    #     print("Resource not found. Please check the endpoint URL and parameters.")
    #     return {"status": "error", "message": "Resource not found"}
    # elif response.status_code == 409:
    #     print("The user email address already exists for this company.")
    #     return {"status": "exists", "message": "User already exists"}
    # else:
    #     print(f"Error: {response.status_code} - {response.text}")
    #     return {"status": "error", "message": response.text}


@tool
def get_users() -> Optional[List[Dict[str, Any]]]:
  """
  Retrieves a list of users from Procore.

  Returns:
      Optional[List[Dict[str, Any]]]: A list of user data if successful, None otherwise
  """
  # Access token and company ID
#   company_id = 4268843
  company_id = os.getenv('PROCORE_COMPANY_ID')
  access_token = os.getenv('access_token') 
  
  # Define the URL for retrieving users
  users_url = f"https://sandbox.procore.com/rest/v1.0/companies/{company_id}/users"

  # Headers for the request
  headers = {
      "Authorization": f"Bearer {access_token}",
      "Accept": "application/json",
      "Content-Type": "application/json"
  }

  # Make the GET request
  response = requests.get(users_url, headers=headers)

  # Check the response status code and body
  print(f"Status Code: {response.status_code}")
  print(f"Response Body: {response.text}")

  if response.status_code == 200:
      users = response.json()
      print("Users retrieved successfully:")
      return users
  elif response.status_code == 404:
      error ="Resource not found. Please check the endpoint URL and parameters."
      print(error)
      return error
  else:
      error = f"Error: {response.status_code} - {response.text}"
      print(error)
      return error    



# Update the where_to_go function to handle existing users
def where_to_go(state):
    messages = state['messages']
    last_message = messages[-1]

    # Check if the last message contains a tool output with "exists" status
    if "exists" in last_message.additional_kwargs.get("tool_output", {}):
        print("User already exists. Moving to end state.")
        return "end"
    elif "function_call" in last_message.additional_kwargs:
        return "continue"
    else:
        return "end"
    
