# from ..tools.initialize_tools import initialize_api_tools
from ..tools.initialize_tools import initialize_api_tools
from ..models.openai_models import load_openai_model  # Import the model loader

# from ..states.state import GraphState, where_to_go
from langchain_core.messages import HumanMessage, AIMessage
from ..prompts.prompts import get_api_handler_system_message
from ..tools.utils_tools import get_search_tool


import json
from typing import Dict, Any
import logging
import streamlit as st
import os
from dotenv import load_dotenv

from langgraph.types import interrupt, Command


# load_dotenv()


# Define search tool
# search = get_search_tool()
useful_endpoints="""
  ('GET /rest/v1.1/projects',
  {'description': 'Return a list of active Projects.
   'parameters': [
    {'name': 'company_id',
     'in': 'query',
     'description': 'Unique identifier for the company.',
     'required': True,
     'schema': {'type': 'integer'}}]}),
  ('GET /rest/v1.3/users',
  {'description': 'Return a list of all Users associated with a Company.
   'parameters': [
   {'name': 'company_id',
     'in': 'query',
     'description': 'Unique identifier for the company.',
     'required': True,
     'schema': {'type': 'integer'}}]}),
    [('POST /rest/v1.0/task_items',
  {'description': 'Creates a task item on a given project',
   'parameters': [
    {'name': 'project_id',
     'in': 'query',
     'description': 'Unique identifier for the project.',
     'required': True,
     'schema': {'type': 'integer'}}],
   'requestBody': {'content': {'application/json': {'schema': {'type': 'object',
       'required': ['task_item'],
       'properties': {'task_item': {'type': 'object',
         'properties': {'title': {'type': 'string',
           'description': 'Title',
           'example': 'Safety audit of sector 7G'},
          'number': {'type': 'string',
           'description': 'Number',
           'example': '1B'},
          'description': {'type': 'string',
           'description': 'Description',
           'example': 'Perform full audit to determine safety compliance in 7G'},
          'due_date': {'type': 'string',
           'format': 'date-time',
           'description': 'Date and time due'},
          'status': {'type': 'string',
           'description': 'Status',
           'enum': ['initiated',
            'in_progress',
            'ready_for_review',
            'closed',
            'void']},
          'task_item_category_id': {'type': 'integer',
           'description': 'The task item category to associate with the task item.'},
          'private': {'type': 'boolean', 'description': 'Privacy flag'},
          'assigned_id': {'type': 'integer', 'description': 'Assignee ID'},
          'assignee_ids': {'type': 'array',
           'description': 'Assignee IDs',
           'items': {'type': 'integer'}},
          'distribution_member_ids': {'type': 'array',
           'description': 'Distribution Member IDs',
           'items': {'type': 'integer'}},
          'attachments': {'type': 'array',
           'description': 'Task Item attachments.\nTo upload attachments you must upload the entire payload as `multipart/form-data` content-type and\nspecify each parameter as form-data together with `attachments[]` as files.',
           'items': {'type': 'string'}},
          'drawing_revision_ids': {'type': 'array',
           'description': 'Drawing Revisions to attach to the response',
           'items': {'type': 'integer'},
           'example': [4, 5]},
          'file_version_ids': {'type': 'array',
           'description': 'File Versions to attach to the response',
           'items': {'type': 'integer'},
           'example': [6, 7]},
          'form_ids': {'type': 'array',
           'description': 'Forms to attach to the response',
           'items': {'type': 'integer'},
           'example': [7, 8]},
          'image_ids': {'type': 'array',
           'description': 'Images to attach to the response',
           'items': {'type': 'integer'},
           'example': [9, 10]},
          'upload_ids': {'type': 'array',
           'description': 'Uploads to attach to the response',
           'items': {'type': 'string'},
           'example': ['4120226e-36a8-416f-970e-880bae78164f',
            'de07e35a-4860-4f96-acd8-8360833dc495']},
          'document_management_document_revision_ids': {'type': 'array',
           'description': 'PDM document to attach to the response',
           'items': {'type': 'string'},
           'example': ['4120226e-36a8-416f-970e-880bae78164f',
            'de07e35a-4860-4f96-acd8-8360833dc495']}}}}}}},
    'required': True}}),   
    """

def APIHandlerAgent(state: Dict[str, Any]) -> Dict[str, Any]:

    # Initialize LLM using function from openai_models.py
    llm = load_openai_model(model="gpt-4o-mini")
    # llm = load_openai_model(model="gpt-4o")

    api_spec_file = 'OAS_updated.json'
    base_url = "https://sandbox.procore.com"
    
    overrides = {"servers": [{"url": base_url}]}

    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    access_token = st.session_state.access_token

    
    company_id=os.getenv("PROCORE_COMPANY_ID")

    tools=initialize_api_tools(company_id,access_token, api_spec_file, overrides)

    llm_with_tools = llm.bind_tools(tools)


    query = state["query"]

    # messages = state["messages"]
    # command = state["command"]
    api_agent_messages = state["api_agent_messages"]
    api_agent_feedback = state["api_agent_feedback"]

    sys_msg = get_api_handler_system_message(company_id, base_url, useful_endpoints)

#================================================================================================
    import yaml
    from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec

    with open("procore_core_openapi.yaml", "r") as file:
        raw_procore_api_spec = yaml.load(file, Loader=yaml.Loader)
    
    # relevent_endpoints = reduce_openapi_spec(raw_procore_api_spec).endpoints
#================================================================================================
    # Initialize feedback strings & metadata
    api_feedback_message = ""

    # Determine tool messages after the last AI response
    try:
        last_ai_index = max(
            i for i, msg in enumerate(api_agent_messages) if msg.type == "ai"
        )
        last_tool_messages = [
            msg
            for msg in api_agent_messages[last_ai_index + 1:]
            if msg.type == "tool"
        ]
    except:

        last_tool_messages = []

    # Process tool messages and gather feedback
    for msg in last_tool_messages:
        if msg.name == "sql_db_query":
            data_frame_metadata = msg.artifact
            api_feedback_message += f"\n tool output: {msg.content}"
        else:
            api_feedback_message += f"\n tool output: {msg.content}"


#     api_handler_prompt = f"""
#   here is the user original query
#   - query: {query}

#   - command to execute: {command}

#     API configuration:
#     Base url: {base_url}
#     User Company id: {company_id}
#     note that you can use the api call to get some messing values needed for the next api call
  
#   """

#     api_handler_prompt = f"""
#   here is the user original query
#   - query: {query}

#     API configuration:
#     Base url: {base_url}
#     User Company id: {company_id}
#   """
    # useful endpoints that you may or may not need to use: {useful_endpoints}
    # note that you can use the api call to get some messing values needed for the next api call,
    # stick with the url from the endpoint list

#     api_handler_prompt = f"""
#   here is the user original query
#   - query: {query}
#   """
    # useful endpoints that you may or may not need to use: {useful_endpoints}
    # note that you can use the api call to get some messing values needed for the next api call,
    # stick with the url from the endpoint list

    message = HumanMessage(content=f"{query}")
    # message = query


    try:
        response = llm_with_tools.invoke([sys_msg, message]+api_agent_messages )


#================================================================================================
# Human in the loop
        # st.write(f"before interrupt")
        # human_review = interrupt(
        #     {
        #         "question": "Would you like to approve this API call?",
        #         "planned_api_call": {
        #             "content": response.content,
        #             "tool_calls": response.tool_calls if hasattr(response, "tool_calls") else None
        #         }
        #     }
        # )
        # st.write(f"after interrupt: {human_review}")

        #review_action, review_data = human_review
        #st.write(f"Review action: {review_action}")

        # # Approve the tool call and continue
        # if review_action == "continue":
        #     return Command(goto="run_tool")

        # if approval:
        #     response = llm_with_tools.invoke([sys_msg, message, approval]+api_agent_messages)
#================================================================================================
        # Capture the model's response
        feedback_message = f"{response.content}"
        api_feedback_message += f"{response.content}"


        # If the response includes any tool calls, append them to feedback
        if hasattr(response, "tool_calls") and response.tool_calls:
            for call in response.tool_calls:
                tool_name = call.get("name")
                tool_args = call.get("args", {})

                if tool_name:
                    feedback_message += f"\nCalling the {tool_name} tool"
                    api_feedback_message += f"\nCalling the {tool_name} tool"
                if tool_args:
                    feedback_message += f" with the following arguments: {tool_args}"
                    api_feedback_message += f" with the following arguments: {tool_args}"

        # Build the return dictionary
        return_dict = {
            "messages": [response],
            "api_agent_messages": [response],
            # "command": command,
            "feedback": [
                {
                    "agent": "api_handler",
                    # "command": command,
                    "response": feedback_message,
                    "status": "Success",
                }
            ],
            "api_agent_feedback": [api_feedback_message],
        }

        return return_dict

    except Exception as e:
        error_msg = HumanMessage(content=str(e))
        return {
            "api_agent_messages": [error_msg],
            # "command": command,
            "feedback": [
                {
                    "status": "error",
                    "step": 2,
                    "message": "API calling failed",
                    "result": {
                        "success": False,
                        "data": None,
                        "message": f"Error making API call: {str(e)}",
                        "error": str(e),
                    },
                }
            ],
        }