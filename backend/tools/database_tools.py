# import json
# import requests
# import os
# import sqlite3
# from typing import List, Dict, Optional
# from datetime import datetime
# from langchain_core.tools import tool

# @tool
# def sync_users_from_procore() -> str:
#     """
#     Fetches the list of users from the Procore API and syncs the data with the local SQLite database.

#     This function retrieves user data, processes it, and inserts it into the 'users' table in the 
#     SQLite database 'procore_db.sqlite'. It ensures that the user data is up-to-date in the database 
#     by adding new records or updating existing ones based on the user ID.

#     Returns:
#         str: A success message if synchronization is completed, or an error message if failed.
#     """
#     company_id = os.getenv('PROCORE_COMPANY_ID')
#     access_token = os.getenv('access_token')

#     # Define the URL for retrieving users
#     users_url = f"https://sandbox.procore.com/rest/v1.0/companies/{company_id}/users"

#     # Headers for the request
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Accept": "application/json",
#         "Content-Type": "application/json"
#     }

#     # Make the GET request
#     response = requests.get(users_url, headers=headers)

#     # Check the response status code and body
#     if response.status_code == 200:
#         users = response.json()

#         # Sync users with SQLite database
#         try:
#             conn = sqlite3.connect('backend/procore_db.sqlite')
#             cursor = conn.cursor()

#             for user in users:
#                 # Prepare user data for insertion or update
#                 user_data = (
#                     user.get("address"),
#                     user.get("avatar"),
#                     user.get("business_id"),
#                     user.get("business_phone"),
#                     user.get("business_phone_extension"),
#                     user.get("city"),
#                     user.get("contact_id"),
#                     user.get("country_code"),
#                     user.get("created_at"),
#                     user.get("email_address"),
#                     user.get("email_signature"),
#                     user.get("employee_id"),
#                     user.get("erp_integrated_accountant"),
#                     user.get("fax_number"),
#                     user.get("first_name"),
#                     user.get("id"),
#                     user.get("initials"),
#                     user.get("is_active"),
#                     user.get("is_employee"),
#                     user.get("job_title"),
#                     user.get("last_activated_at"),
#                     user.get("last_login_at"),
#                     user.get("last_name"),
#                     user.get("mobile_phone"),
#                     user.get("name"),
#                     user.get("notes"),
#                     user.get("origin_id"),
#                     user.get("origin_data"),
#                     user.get("state_code"),
#                     user.get("updated_at"),
#                     user.get("welcome_email_sent_at"),
#                     user.get("zip"),
#                     user.get("work_classification_id"),
#                     json.(user.get("permission_template")),  # JSON field
#                     json.dumps(user.get("company_permission_template")),  # JSON field
#                     json.dumps(user.get("vendor")),  # JSON field
#                     user.get("role"),
#                     user.get("verified_employee")
#                 )

#                 # SQL command for inserting or updating the user record
#                 cursor.execute("""
#                     INSERT INTO users (
#                         address, avatar, business_id, business_phone, business_phone_extension, 
#                         city, contact_id, country_code, created_at, email_address, email_signature, 
#                         employee_id, erp_integrated_accountant, fax_number, first_name, id, initials, 
#                         is_active, is_employee, job_title, last_activated_at, last_login_at, last_name, 
#                         mobile_phone, name, notes, origin_id, origin_data, state_code, updated_at, 
#                         welcome_email_sent_at, zip, work_classification_id, permission_template, 
#                         company_permission_template, vendor, role, verified_employee
#                     ) 
#                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
#                     ON CONFLICT(id) DO UPDATE SET
#                         address=excluded.address,
#                         avatar=excluded.avatar,
#                         business_id=excluded.business_id,
#                         business_phone=excluded.business_phone,
#                         business_phone_extension=excluded.business_phone_extension,
#                         city=excluded.city,
#                         contact_id=excluded.contact_id,
#                         country_code=excluded.country_code,
#                         created_at=excluded.created_at,
#                         email_address=excluded.email_address,
#                         email_signature=excluded.email_signature,
#                         employee_id=excluded.employee_id,
#                         erp_integrated_accountant=excluded.erp_integrated_accountant,
#                         fax_number=excluded.fax_number,
#                         first_name=excluded.first_name,
#                         initials=excluded.initials,
#                         is_active=excluded.is_active,
#                         is_employee=excluded.is_employee,
#                         job_title=excluded.job_title,
#                         last_activated_at=excluded.last_activated_at,
#                         last_login_at=excluded.last_login_at,
#                         last_name=excluded.last_name,
#                         mobile_phone=excluded.mobile_phone,
#                         name=excluded.name,
#                         notes=excluded.notes,
#                         origin_id=excluded.origin_id,
#                         origin_data=excluded.origin_data,
#                         state_code=excluded.state_code,
#                         updated_at=excluded.updated_at,
#                         welcome_email_sent_at=excluded.welcome_email_sent_at,
#                         zip=excluded.zip,
#                         work_classification_id=excluded.work_classification_id,
#                         permission_template=excluded.permission_template,
#                         company_permission_template=excluded.company_permission_template,
#                         vendor=excluded.vendor,
#                         role=excluded.role,
#                         verified_employee=excluded.verified_employee
#                 """, user_data)

#             # Commit changes and close the connection
#             conn.commit()
#             conn.close()

#             return "Users synchronized successfully with the database."

#         except Exception as e:
#             return f"Error occurred while syncing users: {str(e)}"
#     else:
#         return f"Failed to retrieve users: {response.status_code} - {response.text}"


import json
import requests
import os
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from langchain_core.tools import tool

@tool
def sync_users_from_procore() -> str:
  """
  Fetches the list of users from the Procore API and syncs the data with the local SQLite database.
  Required fields are email_address and last_name, while other fields are optional.

  Returns:
      str: A success message if synchronization is completed, or an error message if failed.
  """
  company_id = os.getenv('PROCORE_COMPANY_ID')
  access_token = os.getenv('access_token')

  users_url = f"https://sandbox.procore.com/rest/v1.0/companies/{company_id}/users"
  headers = {
      "Authorization": f"Bearer {access_token}",
      "Accept": "application/json",
      "Content-Type": "application/json"
  }

  response = requests.get(users_url, headers=headers)

  if response.status_code == 200:
      users = response.json()

      try:
          conn = sqlite3.connect('backend/procore_db.sqlite')
          cursor = conn.cursor()

          # Create table if it doesn't exist with required fields marked as NOT NULL
          cursor.execute("""
              CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY,
                  email_address TEXT NOT NULL,
                  last_name TEXT NOT NULL,
                  address TEXT,
                  avatar TEXT,
                  business_id INTEGER,
                  business_phone TEXT,
                  business_phone_extension TEXT,
                  city TEXT,
                  contact_id INTEGER,
                  country_code TEXT,
                  created_at TEXT,
                  email_signature TEXT,
                  employee_id TEXT,
                  erp_integrated_accountant BOOLEAN,
                  fax_number TEXT,
                  first_name TEXT,
                  initials TEXT,
                  is_active BOOLEAN,
                  is_employee BOOLEAN,
                  job_title TEXT,
                  last_activated_at TEXT,
                  last_login_at TEXT,
                  mobile_phone TEXT,
                  name TEXT,
                  notes TEXT,
                  origin_id TEXT,
                  origin_data TEXT,
                  state_code TEXT,
                  updated_at TEXT,
                  welcome_email_sent_at TEXT,
                  zip TEXT,
                  work_classification_id INTEGER,
                  permission_template TEXT,
                  company_permission_template TEXT,
                  vendor TEXT,
                  role TEXT,
                  verified_employee BOOLEAN
              )
          """)

          for user in users:
              # Validate required fields
              email = user.get("email_address")
              last_name = user.get("last_name")
              
              if not email or not last_name:
                  print(f"Skipping user record - missing required fields: {user}")
                  continue

              # Map all available fields from the response
              user_data = {
                  field: user.get(field) for field in [
                      "address", "avatar", "business_id", "business_phone",
                      "business_phone_extension", "city", "contact_id", "country_code",
                      "created_at", "email_address", "email_signature", "employee_id",
                      "erp_integrated_accountant", "fax_number", "first_name", "id",
                      "initials", "is_active", "is_employee", "job_title",
                      "last_activated_at", "last_login_at", "last_name", "mobile_phone",
                      "name", "notes", "origin_id", "origin_data", "state_code",
                      "updated_at", "welcome_email_sent_at", "zip",
                      "work_classification_id", "role", "verified_employee"
                  ]
              }

              # Handle JSON fields
              user_data["permission_template"] = json.dumps(user.get("permission_template"))
              user_data["company_permission_template"] = json.dumps(user.get("company_permission_template"))
              user_data["vendor"] = json.dumps(user.get("vendor"))

              # Create placeholders and values for SQL query
              fields = ", ".join(user_data.keys())
              placeholders = ", ".join(["?" for _ in user_data])
              values = tuple(user_data.values())

              # Generate the UPDATE part of the query
              update_fields = ", ".join([f"{k}=excluded.{k}" for k in user_data.keys()])

              # SQL command for inserting or updating the user record
              sql = f"""
                  INSERT INTO users ({fields})
                  VALUES ({placeholders})
                  ON CONFLICT(id) DO UPDATE SET
                  {update_fields}
              """
              
              cursor.execute(sql, values)

          conn.commit()
          conn.close()
          return "Users synchronized successfully with the database."
          # return {"sql_agent_messages":"Users synchronized successfully with the database."}

      except Exception as e:
          return f"Error occurred while syncing users: {str(e)}"
  else:
      return f"Failed to retrieve users: {response.status_code} - {response.text}"