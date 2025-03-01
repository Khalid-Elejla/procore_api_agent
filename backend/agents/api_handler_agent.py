# # main.py
# import os
# import logging
# from typing import Dict, Any

# import streamlit as st
# from dotenv import load_dotenv
# from langchain_core.messages import HumanMessage

# from ..models.openai_models import load_openai_model
# from ..prompts.prompts import get_api_handler_system_message
# from ..tools.initialize_tools import initialize_api_tools
# from ..tools.utils_tools import get_search_tool

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Load environment variables
# load_dotenv()

# USEFUL_ENDPOINTS="""
#   ('GET /rest/v1.1/projects',
#   {'description': 'Return a list of active Projects.
#    'parameters': [
#     {'name': 'company_id',
#      'in': 'query',
#      'description': 'Unique identifier for the company.',
#      'required': True,
#      'schema': {'type': 'integer'}}]}),
#   ('GET /rest/v1.3/users',
#   {'description': 'Return a list of all Users associated with a Company.
#    'parameters': [
#    {'name': 'company_id',
#      'in': 'query',
#      'description': 'Unique identifier for the company.',
#      'required': True,
#      'schema': {'type': 'integer'}}]}),
#     [('POST /rest/v1.0/task_items',
#   {'description': 'Creates a task item on a given project',
#    'parameters': [
#     {'name': 'project_id',
#      'in': 'query',
#      'description': 'Unique identifier for the project.',
#      'required': True,
#      'schema': {'type': 'integer'}}],
#    'requestBody': {'content': {'application/json': {'schema': {'type': 'object',
#        'required': ['task_item'],
#        'properties': {'task_item': {'type': 'object',
#          'properties': {'title': {'type': 'string',
#            'description': 'Title',
#            'example': 'Safety audit of sector 7G'},
#           'number': {'type': 'string',
#            'description': 'Number',
#            'example': '1B'},
#           'description': {'type': 'string',
#            'description': 'Description',
#            'example': 'Perform full audit to determine safety compliance in 7G'},
#           'due_date': {'type': 'string',
#            'format': 'date-time',
#            'description': 'Date and time due'},
#           'status': {'type': 'string',
#            'description': 'Status',
#            'enum': ['initiated',
#             'in_progress',
#             'ready_for_review',
#             'closed',
#             'void']},
#           'task_item_category_id': {'type': 'integer',
#            'description': 'The task item category to associate with the task item.'},
#           'private': {'type': 'boolean', 'description': 'Privacy flag'},
#           'assigned_id': {'type': 'integer', 'description': 'Assignee ID'},
#           'assignee_ids': {'type': 'array',
#            'description': 'Assignee IDs',
#            'items': {'type': 'integer'}},
#           'distribution_member_ids': {'type': 'array',
#            'description': 'Distribution Member IDs',
#            'items': {'type': 'integer'}},
#           'attachments': {'type': 'array',
#            'description': 'Task Item attachments.\nTo upload attachments you must upload the entire payload as `multipart/form-data` content-type and\nspecify each parameter as form-data together with `attachments[]` as files.',
#            'items': {'type': 'string'}},
#           'drawing_revision_ids': {'type': 'array',
#            'description': 'Drawing Revisions to attach to the response',
#            'items': {'type': 'integer'},
#            'example': [4, 5]},
#           'file_version_ids': {'type': 'array',
#            'description': 'File Versions to attach to the response',
#            'items': {'type': 'integer'},
#            'example': [6, 7]},
#           'form_ids': {'type': 'array',
#            'description': 'Forms to attach to the response',
#            'items': {'type': 'integer'},
#            'example': [7, 8]},
#           'image_ids': {'type': 'array',
#            'description': 'Images to attach to the response',
#            'items': {'type': 'integer'},
#            'example': [9, 10]},
#           'upload_ids': {'type': 'array',
#            'description': 'Uploads to attach to the response',
#            'items': {'type': 'string'},
#            'example': ['4120226e-36a8-416f-970e-880bae78164f',
#             'de07e35a-4860-4f96-acd8-8360833dc495']},
#           'document_management_document_revision_ids': {'type': 'array',
#            'description': 'PDM document to attach to the response',
#            'items': {'type': 'string'},
#            'example': ['4120226e-36a8-416f-970e-880bae78164f',
#             'de07e35a-4860-4f96-acd8-8360833dc495']}}}}}}},
#     'required': True}}),   
#     """

# def initialize_api_config() -> dict:
#     """Initialize API configuration from environment and session state"""
#     return {
#         "api_spec_file": os.getenv("PROCORE_API_SPEC_FILE"),
#         "base_url": os.getenv("PROCORE_API_BASE_URL"),
#         "company_id": os.getenv("PROCORE_COMPANY_ID"),
#         "access_token": st.session_state.get("access_token")
#     }

# def process_tool_messages(messages: list) -> str:
#     """Process tool messages and generate feedback"""
#     try:
#         last_ai_index = max(
#             i for i, msg in enumerate(messages) if msg.type == "ai"
#         )
#         return "\n".join(
#             f"tool output: {msg.content}"
#             for msg in messages[last_ai_index + 1:]
#             if msg.type == "tool"
#         )
#     except ValueError:
#         return ""

# def handle_api_response(response: Any) -> dict:
#     """Process the LLM response and format return structure"""
#     feedback_message = response.content
#     api_feedback_message = feedback_message

#     if hasattr(response, "tool_calls") and response.tool_calls:
#         for call in response.tool_calls:
#             tool_name = call.get("name")
#             tool_args = call.get("args", {})
            
#             feedback_message += f"\nCalling the {tool_name} tool"
#             api_feedback_message += f"\nCalling the {tool_name} tool"
            
#             if tool_args:
#                 args_str = ", ".join(f"{k}: {v}" for k, v in tool_args.items())
#                 feedback_message += f" with arguments: {args_str}"
#                 api_feedback_message += f" with arguments: {args_str}"

#     return {
#         "messages": [response],
#         "api_agent_messages": [response],
#         "feedback": [{
#             "agent": "api_handler",
#             "response": feedback_message,
#             "status": "Success",
#         }],
#         "api_agent_feedback": [api_feedback_message],
#     }

# def APIHandlerAgent(state: Dict[str, Any]) -> Dict[str, Any]:
#     """Handle API operations using LLM and configured tools"""
#     try:
#         # Initialize configuration and models
#         config = initialize_api_config()
#         llm = load_openai_model(model="gpt-4o")
        
#         # Initialize API tools
#         tools = initialize_api_tools(
#             config["company_id"],
#             config["access_token"],
#             config["api_spec_file"],
#             {"servers": [{"url": config["base_url"]}]}
#         )
        
#         # Prepare messages and system prompt
#         llm_with_tools = llm.bind_tools(tools)
#         sys_msg = get_api_handler_system_message(
#             config["company_id"],
#             config["base_url"],
#             USEFUL_ENDPOINTS
#         )

#         # human_message = HumanMessage(content=state["query"])

#         # Extract the text content from the query
#         message_content = state["query"][0].content if isinstance(state["query"], list) else state["query"]
#         human_message = HumanMessage(content=message_content)



#         # Process existing messages
#         api_feedback = process_tool_messages(state["api_agent_messages"])
        
#         # Invoke LLM
#         response = llm_with_tools.invoke(
#             [sys_msg, human_message] + state["api_agent_messages"]
#         )
        
#         return handle_api_response(response)

#     except Exception as e:
#         logger.error(f"API handling failed: {str(e)}", exc_info=True)
#         return {
#             "api_agent_messages": [HumanMessage(content=str(e))],
#             "feedback": [{
#                   "agent": "planner",
#                   "action": "Generate a plan to address the user's request.",
#                   "response": f"Error in plan generation. Please refine your query.",
#                   "status": "Error"
#               }]
#=======================================================================================================================================================================
##################WORKING BUT FULL HISTORY INCLUDED WITH REDUNDUNT USER MESSAGE
import os
import logging
from typing import Dict, Any

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from ..models.openai_models import load_openai_model
from ..prompts.prompts import get_api_handler_system_message
from ..tools.initialize_tools import initialize_api_tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

USEFUL_ENDPOINTS = """
[Same endpoint definitions as original]
"""

def initialize_api_config() -> dict:
    """Initialize API configuration from environment and session state"""
    return {
        "api_spec_file": os.getenv("PROCORE_API_SPEC_FILE"),
        "base_url": os.getenv("PROCORE_API_BASE_URL"),
        "company_id": os.getenv("PROCORE_COMPANY_ID"),
        "access_token": st.session_state.get("access_token")
    }

def process_tool_messages(messages: list) -> str:
    """Process tool messages and generate feedback"""
    try:
        last_ai_index = max(
            i for i, msg in enumerate(messages) if isinstance(msg, HumanMessage)
        )
        return "\n".join(
            f"tool output: {msg.content}"
            for msg in messages[last_ai_index + 1:]
            if isinstance(msg, SystemMessage)  # Adjust based on actual tool message type
        )
    except ValueError:
        return ""

def handle_api_response(response: Any, human_message: HumanMessage) -> dict:
    """Process the LLM response and format return structure"""
    feedback_message = response.content
    api_feedback_message = feedback_message

    if hasattr(response, "tool_calls") and response.tool_calls:
        for call in response.tool_calls:
            tool_name = call.get("name")
            tool_args = call.get("args", {})
            
            feedback_message += f"\nCalling the {tool_name} tool"
            api_feedback_message += f"\nCalling the {tool_name} tool"
            
            if tool_args:
                args_str = ", ".join(f"{k}: {v}" for k, v in tool_args.items())
                feedback_message += f" with arguments: {args_str}"
                api_feedback_message += f" with arguments: {args_str}"

    return {
        "messages": [response],
        "feedback": [{
            "agent": "api_handler",
            "response": feedback_message,
            "status": "Success",
        }],
        "api_agent_feedback": [api_feedback_message],        
    }

def APIHandlerAgent(state: Dict[str, Any]) -> Dict[str, Any]:
    """Handle API operations using LLM and configured tools"""
    try:
        # Initialize configuration and models
        config = initialize_api_config()
        llm = load_openai_model(model="gpt-4o")
        
        # Initialize API tools
        tools = initialize_api_tools(
            config["company_id"],
            config["access_token"],
            config["api_spec_file"],
            {"servers": [{"url": config["base_url"]}]}
        )
        
        # Prepare messages and system prompt
        llm_with_tools = llm.bind_tools(tools)
        sys_msg = get_api_handler_system_message(
            config["company_id"],
            config["base_url"],
            USEFUL_ENDPOINTS
        )

        # Extract the text content from the query
        message_content = state["query"][0].content if isinstance(state["query"], list) else state["query"]
        human_message = HumanMessage(content=message_content)


        # Prepare message history
        conversation_history = state.get("api_agent_messages", [])
        
        # Add system message only if not present
        if not any(isinstance(msg, SystemMessage) for msg in conversation_history):
            conversation_history = [sys_msg] + conversation_history

        # Build message list
        messages = conversation_history[-10:] + [human_message]

        # Process existing tool messages
        api_feedback = process_tool_messages(messages)
        
        # Invoke LLM with proper message order
        response = llm_with_tools.invoke(messages)
        
        # Update conversation history
#        new_messages = conversation_history + [human_message, response]
        new_messages = [human_message, response]
        
        return {
            **handle_api_response(response, human_message),
            "api_agent_messages": new_messages,
        }

    except Exception as e:
        logger.error(f"API handling failed: {str(e)}", exc_info=True)
        error_message = HumanMessage(content=f"Error: {str(e)}")
        return {
            "api_agent_messages": state.get("api_agent_messages", []) + [human_message, error_message],
            "feedback": [{
                "agent": "api_handler",
                "response": f"API operation failed: {str(e)}",
                "status": "Error"
            }]
        }

#============================================================================================================================================================
