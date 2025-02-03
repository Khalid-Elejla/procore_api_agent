import os
import requests
from typing import Optional, Dict, Any, List
from langchain_core.tools import tool

# =============================================add project============================================= #
@tool
def create_project(
    project_name: str,
    description: str,
    start_date: str,
    end_date: str
) -> Optional[Dict[str, Any]]:
    """
    Creates a new project in Procore with the given details.

    Parameters:
        project_name (str): The name of the project to create
        description (str): A description of the project
        start_date (str): The start date of the project in YYYY-MM-DD format
        end_date (str): The end date of the project in YYYY-MM-DD format

    Returns:
        Optional[Dict[str, Any]]: The created project data if successful, None otherwise
    """
    #access_token="eyJhbGciOiJFUzUxMiJ9.eyJhbXIiOltdLCJhaWQiOiJKVGxVcl9uZWljeUhvampiTHBTdTVYa0VIam9EOG1PR2hIY0xEUzhzY3k4IiwiYW91aWQiOm51bGwsImFvdXVpZCI6bnVsbCwiZXhwIjoxNzI5NzIyMjgzLCJzaWF0IjoxNzI5NjI4ODYyLCJ1aWQiOjEzOTI1NiwidXVpZCI6ImRhNjA2MmVmLWFmMGItNDdkYS05YjAzLWU1ZTcxYTg0MWQwNyIsImxhc3RfbWZhX2NoZWNrIjoxNzI5NzE2ODgzfQ.AEUN3BFh9uyb_YGOqRH6u5Iw3z5V80v2kcvGT2MgB-FS5GKuk1fqnHwlGS22QUpB0WR_YWa9kXgkQSED2asTqbIVAWqYGb3H505wb8SBIx0_CgAEgIfUkANBAEzomGhZ1pfajCe00rdBsf7Dj8Ud1sviqtMFbt1KYdU6viQtEJDbgeY6"
    # access_token= "eyJhbGciOiJFUzUxMiJ9.eyJhbXIiOltdLCJhaWQiOiJKVGxVcl9uZWljeUhvampiTHBTdTVYa0VIam9EOG1PR2hIY0xEUzhzY3k4IiwiYW91aWQiOm51bGwsImFvdXVpZCI6bnVsbCwiZXhwIjoxNzI5NjY5MjMwLCJzaWF0IjoxNzI5NjI4ODYyLCJ1aWQiOjEzOTI1NiwidXVpZCI6ImRhNjA2MmVmLWFmMGItNDdkYS05YjAzLWU1ZTcxYTg0MWQwNyIsImxhc3RfbWZhX2NoZWNrIjoxNzI5NjYzODMwfQ.AOFqN3MVHIL6sC_Jak99TRHIVVFd_FUqRRWvVzgJz5RDddQd6xylfPSpsLjiGd62UzSmYh1sp9Wd23jyXmytR_fCAGI__hdzxCsHLN79U5T3E_5sJfYaD8NAIkTkEUuwFa1oX4WWcb8pqaNMMWzH0qVG_ITaWdE5hImDFsqfUybuyfHc"
    company_id = os.getenv('PROCORE_COMPANY_ID')
    access_token = os.getenv('access_token') 

    # Define the URL for project creation
    projects_url = "https://sandbox.procore.com/rest/v1.0/projects"


    # Headers for the request
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Procore-Company-Id": str(company_id)  # Add Procore-Company-Id header
    }

    # Payload for the new project
    payload = {
        "name": project_name,
        "company_id": company_id,  # This should match your company ID
        "description": description,
        "start_date": start_date,  # Format: YYYY-MM-DD
        "end_date": end_date  # Format: YYYY-MM-DD
    }

    # Make the POST request
    response = requests.post(projects_url, headers=headers, json=payload)

    # Check the response status code and body
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 201:
        project = response.json()
        print("Project created successfully:")
        return project
    elif response.status_code == 404:
        error_msg="Resource not found. Please check the endpoint URL and parameters."
        print(error_msg)
        return error_msg
    else:
        error_msg=f"Error: {response.status_code} - {response.text}"
        print(error_msg)
        return error_msg
    

# =============================================get project information============================================= #
@tool
def get_projects() -> Optional[List[Dict[str, Any]]]:
  """
  Retrieves all projects from Procore.

  Returns:
      Optional[List[Dict[str, Any]]]: A list of project dictionaries if successful, None otherwise
  """
  
  # access_token = "eyJhbGciOiJFUzUxMiJ9.eyJhbXIiOltdLCJhaWQiOiJKVGxVcl9uZWljeUhvampiTHBTdTVYa0VIam9EOG1PR2hIY0xEUzhzY3k4IiwiYW91aWQiOm51bGwsImFvdXVpZCI6bnVsbCwiZXhwIjoxNzI5Njc1MTkxLCJzaWF0IjoxNzI5NjI4ODYyLCJ1aWQiOjEzOTI1NiwidXVpZCI6ImRhNjA2MmVmLWFmMGItNDdkYS05YjAzLWU1ZTcxYTg0MWQwNyIsImxhc3RfbWZhX2NoZWNrIjoxNzI5NjY5NzkxfQ.Aflf-VxIbour66LbSS-vVZ6Y_lWOm96lhCJP97LRBv5xvVWjCYNOVgpGxjpzWjJIpy9jQ0Z17zdV2kwpAPAj9ocqAeCCL87FD9GsNkxAxJC-_IE65Qcq9C0AdGx-RsH7i9RD_bjrL9Y5w6bHZ_Oz7X5mfCfFmN4sSSyeAt1_Xg0BM6Cj"
  company_id = 4268843
  
  # Define the URL for getting projects
  projects_url = "https://sandbox.procore.com/rest/v1.0/projects"

  # Headers for the request
  headers = {
      "Authorization": f"Bearer {access_token}",
      "Accept": "application/json",
      "Procore-Company-Id": str(company_id)
  }

  # Optional query parameters
  params = {
      "company_id": company_id,
      # You can add more query parameters as needed:
      # "page": 1,
      # "per_page": 100,
      # "filters[active]": "true"
  }

  try:
      # Make the GET request
      response = requests.get(projects_url, headers=headers, params=params)

      # Check the response status code and body
      print(f"Status Code: {response.status_code}")
      print(f"Response Body: {response.text}")

    #   if response.status_code == 200:
    #       projects = response.json()
    #       print(f"Successfully retrieved {len(projects)} projects")
    #       return projects

      if response.status_code == 200:
      # Check if the response contains an error message in the JSON
        try:
            response_data = response.json()
            if 'error' in response_data:
                print("yes error")
                # If there is an error field in the response
                error_msg = f"Error: {response_data['error']}"
                print(error_msg)
                return {"error": error_msg}
            # If no error, process the data as normal
            projects = response_data
            print(f"Successfully retrieved {len(projects)} projects")
            return {"projects": projects}
        except ValueError:
            # If the response isn't valid JSON
            error_msg = "Failed to parse the response body as JSON."
            print(error_msg)
            return {"error": error_msg}

      elif response.status_code == 404:
          error_msg="Resource not found. Please check the endpoint URL and parameters."
          print(error_msg)
          return error_msg
      else:
          error_msg=f"Error: {response.status_code} - {response.text}"
          print(error_msg)
          return error_msg

  except requests.exceptions.RequestException as e:
      error_msg=f"An error occurred while making the request: {str(e)}"
      print(error_msg)
      return error_msg
  
# =============================================get project information============================================= #
@tool
def rename_project(
  current_project_name: str,
  new_project_name: str
) -> Optional[Dict[str, Any]]:
  """
  Renames an existing project in Procore.

  Parameters:
      current_project_name (str): The current name of the project you want to rename.
      new_project_name (str): The new name you want to assign to the project.

  Returns:
      Optional[Dict[str, Any]]: The updated project data if successful, None otherwise.
  """

  #access_token="eyJhbGciOiJFUzUxMiJ9.eyJhbXIiOltdLCJhaWQiOiJKVGxVcl9uZWljeUhvampiTHBTdTVYa0VIam9EOG1PR2hIY0xEUzhzY3k4IiwiYW91aWQiOm51bGwsImFvdXVpZCI6bnVsbCwiZXhwIjoxNzI5NzIzMDQ2LCJzaWF0IjoxNzI5NjI4ODYyLCJ1aWQiOjEzOTI1NiwidXVpZCI6ImRhNjA2MmVmLWFmMGItNDdkYS05YjAzLWU1ZTcxYTg0MWQwNyIsImxhc3RfbWZhX2NoZWNrIjoxNzI5NzE3NjQ2fQ.AOZI-a0SLPwGKW5fvnPwXc_udijOgCzxnvPmYzI5saYaHvZBYGJycIPwvDbxrWaqbo3hHVzcgxv3a0BS47B6FD4qAZ6EEF7tSn5AwAlnA68s3P0B_2xcWcQ1wlrOt2l5EawslGRtzmeCa-VXCG2OinFWV4nCXC3gDSb-IGQXbPJj5U16"
  company_id = 4268843  # Replace with your company ID

  # Headers for the request
  headers = {
      "Authorization": f"Bearer {access_token}",
      "Accept": "application/json",
      "Content-Type": "application/json",
      "Procore-Company-Id": str(company_id)
  }

  # Step 1: Get the list of projects to find the project ID
  projects_url = "https://sandbox.procore.com/rest/v1.0/projects"

  params = {
      "company_id": company_id
  }

  response = requests.get(projects_url, headers=headers, params=params)

  if response.status_code == 200:
      projects = response.json()

      # Find the project with the current_project_name
      project_id = None
      for project in projects:
          if project.get('name') == current_project_name:
              project_id = project.get('id')
              break

      if project_id is None:
          print(f"Project with name '{current_project_name}' not found.")
          return None
  else:
      print(f"Error fetching projects: {response.status_code} - {response.text}")
      return None

  # Step 2: Update the project's name
  update_url = f"https://sandbox.procore.com/rest/v1.0/projects/{project_id}"

  payload = {
      "name": new_project_name
  }

  response = requests.put(update_url, headers=headers, json=payload, params={"company_id": company_id})

  if response.status_code == 200:
      updated_project = response.json()
      print("Project renamed successfully:")
      return updated_project
  else:
      print(f"Error updating project: {response.status_code} - {response.text}")
      return None
