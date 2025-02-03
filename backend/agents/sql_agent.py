from ..models.openai_models import load_openai_model  # Import the model loader

# from ..states.state import GraphState, where_to_go
from langchain_core.messages import HumanMessage
from ..prompts.prompts import get_sql_agent_system_message
from ..tools.utils_tools import get_search_tool
from ..tools.procore_toolset.users_tools import create_user, get_users
from ..tools.database_tools import sync_users_from_procore
from ..tools.database_toolkit import CustomSQLDatabaseToolkit
from ..tools.dataframe_manager import DataFrameManager
import json
from typing import TypedDict, Annotated, List, Tuple, Dict, Any

from langchain_community.utilities import SQLDatabase

from ..tools.initialize_tools import initialize_db_tools


# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit


# # Initialize LLM using function from openai_models.py
# llm = load_openai_model()
# df_manager = DataFrameManager()

# db = SQLDatabase.from_uri("sqlite:///./backend/procore_db.sqlite")
# # toolkit = SQLDatabaseToolkit(db=db, llm=llm)
# toolkit = CustomSQLDatabaseToolkit(db=db, llm=llm, tools_kwargs={"df_manager": df_manager})  # df_manager only needed here)


# database_tools = toolkit.get_tools()




df_manager = DataFrameManager()
database_tools = initialize_db_tools(db_uri="sqlite:///backend\\procore_db.sqlite", df_manager= df_manager)
llm = load_openai_model()
llm_with_tools = llm.bind_tools(database_tools)

#=========================================================================
  
# def SQLAgent(state: Dict[str, Any]) -> Dict[str, Any]:
#   """
#   SQL agent that executes database queries and returns structured results.
#   """
#   query = state["query"]
#   messages = state["messages"]
#   command=state["command"]
#   sql_agent_messages=state["sql_agent_messages"]


#   # Create system message
#   sys_msg = get_sql_agent_system_message(dialect="SQLite", top_k=20) #, command=command)


#   try:
#       response = llm_with_tools.invoke([sys_msg] + sql_agent_messages + [command])

#       tool_name=None
#       tool_args=None
      
#       feedback_message = f"{response.content}"
  
#       # Check if 'tool_calls' exists and is not empty at the top level
#       if hasattr(response, "tool_calls") and response.tool_calls:
#           tool_calls = response.tool_calls
#         #   feedback_message = f"{response.content}"

#           # Loop through all tool calls to append their details to the feedback message
#           for call in tool_calls:
#               tool_name = call.get("name")
#               tool_args = call.get("args")
              
#               if tool_name:
#                   feedback_message += f" calling the {tool_name} tool"
#               if tool_args:
#                   feedback_message += f" with the following arguments: {tool_args}"

#       return {
#           # "messages": [response],
#           "sql_agent_messages":[response],
#           "command": command,
#       #   "feedback": [{
#       #       "status": "success",
#       #       "step": 2,
#       #       "message": "SQL query execution completed",
#       #       "result": result_data
#       #   }]
#           "feedback": [{
#               "agent": "sql_agent",
#               "command":command,
#               "response": feedback_message,
#               # "response": f"{response.content}" + (f" calling the {tool_name} tool" if tool_name else "") + (f" with the following arguments: {tool_args}" if tool_args else ""),
#               "status": "Success",
#           }]
#       }

#   except Exception as e:
#       result_data = {
#           "success": False,
#           "data": None,
#           "message": f"Error executing SQL query: {str(e)}",
#           "error": str(e)
#       }

#       error_msg = HumanMessage(content=str(e))
#       return {
#           "sql_agent_messages":[error_msg],
#           "command": command,
#           # "messages": [error_msg],
#           "feedback": [{
#               "status": "error",
#               "step": 2,
#               "message": "SQL execution failed",
#               "result": result_data
#           }]
#       }

#======================================================================================================================================
# from typing import TypedDict, Dict, Optional
# import pandas as pd
# from states.state import SQLState

# def SQLAgent(state: Dict[str, Any]) -> Dict[str, Any]:
#     """
#     SQL agent that executes database queries and returns structured results.
#     """
#     query = state["query"]
#     messages = state["messages"]
#     command = state["command"]
#     sql_agent_messages = state["sql_agent_messages"]

#     # Initialize SQL state if not exists
#     sql_state: SQLState = state.get("sql_state", {"tables": {}, "status": None})

#     # Create system message
#     sys_msg = get_sql_agent_system_message(dialect="SQLite", top_k=20)

#     try:
#         response = llm_with_tools.invoke([sys_msg] + sql_agent_messages + [command])
#         feedback_message = f"{response.content}"

#         # Handle tool calls and store results
#         if hasattr(response, "tool_calls") and response.tool_calls:
#             tool_calls = response.tool_calls

#             for call in tool_calls:
#                 tool_name = call.get("name")
#                 tool_args = call.get("args")

#                 # Add tool call details to feedback
#                 if tool_name:
#                     feedback_message += f" calling the {tool_name} tool"
#                 if tool_args:
#                     feedback_message += f" with the following arguments: {tool_args}"

#                 # If the tool call returns data, store it in sql_state
#                 if tool_name == "sql_db_query":
#                     # Assuming the tool execution returns a DataFrame
#                     # You'll need to adapt this based on your actual tool implementation
#                     result_df = execute_tool_call(tool_name, tool_args)  # This is a placeholder

#                     # Extract table name from the query/args
#                     # This is a simplified example - you might need more sophisticated parsing
#                     table_name = extract_table_name(tool_args)  # This is a placeholder

#                     # Store the result in sql_state
#                     sql_state["tables"][table_name] = {
#                         "data": result_df,
#                         "table_name": table_name,
#                         "comment": f"Query result from {command}"
#                     }

#         sql_state["status"] = "success"

#         return {
#             "sql_agent_messages": [response],
#             "command": command,
#             "sql_state": sql_state,  # Add the SQL state to the return
#             "feedback": [{
#                 "agent": "sql_agent",
#                 "command": command,
#                 "response": feedback_message,
#                 "status": "Success",
#             }]
#         }

#     except Exception as e:
#         sql_state["status"] = "error"
#         error_msg = HumanMessage(content=str(e))

#         return {
#             "sql_agent_messages": [error_msg],
#             "command": command,
#             "sql_state": sql_state,
#             "feedback": [{
#                 "status": "error",
#                 "step": 2,
#                 "message": "SQL execution failed",
#                 "result": {
#                     "success": False,
#                     "data": None,
#                     "message": f"Error executing SQL query: {str(e)}",
#                     "error": str(e)
#                 }
#             }]
#         }

# # Placeholder functions that you'll need to implement
# def execute_tool_call(tool_name: str, tool_args: dict) -> pd.DataFrame:
#     """
#     Execute the tool call and return the result as a DataFrame
#     """
#     # Implement based on your actual tool implementation
#     pass

# def extract_table_name(tool_args: dict) -> str:
#     """
#     Extract table name from tool arguments
#     """
#     # Implement based on your query parsing needs
#     pass

#=========================================================================================================================================

from typing import TypedDict, Dict, Optional
import pandas as pd
from langchain.schema import SystemMessage, HumanMessage
from ..states.state import DataFrameMetadata
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

import logging

#=============================================================================
def parse_agent_messages(messages):
    """
    Parses and processes messages in a conversation.

    Args:
        messages (list): List of LangChain message objects 
                        (HumanMessage, AIMessage, ToolMessage).
    """
    for msg in messages:
        # User (HumanMessage)
        if isinstance(msg, HumanMessage):
            print(f"User: {msg.content}\n")

        # AI Agent (AIMessage)
        elif isinstance(msg, AIMessage):
            if 'tool_calls' in msg.additional_kwargs and msg.additional_kwargs['tool_calls']:
                print("Agent is deciding to use tools...\n")
                for tool_call in msg.additional_kwargs['tool_calls']:
                    tool_name = tool_call['function']['name']
                    arguments = tool_call['function']['arguments']
                    print(f"Agent calls tool: {tool_name} with arguments {arguments}\n")
            else:
                print(f"Agent's Final Response:\n{msg.content}\n")

        # Tool Response (ToolMessage)
        elif isinstance(msg, ToolMessage):
            tool_name = msg.name
            print(f"Tool [{tool_name}] Response:\n{msg.content}\n")

        # Unknown Message Type
        else:
            print(f"Unknown message type: {msg}\n")

#=============================================================================
def format_feedback(db_feedback, sql_feedback):
    formatted_output = []

    # Handle DB Agent Feedback
    if db_feedback and len(db_feedback) > 0:
        for item in db_feedback:
            formatted_output.append(f"{item}")

    # Handle SQL Feedback
    if sql_feedback and sql_feedback.strip():
        formatted_output.append(f"{sql_feedback}")

    # If no feedback available
    if not formatted_output:
        formatted_output.append("No feedback available")

    # formatted_output.append("\n**************************************************\n")


    return "\n".join(formatted_output)

def SQLAgent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    SQL agent that executes database queries and returns structured results using SQLDatabaseToolkit.
    """

    import streamlit as st

    # Extract parameters from the state
    query = state["query"]
    messages = state["messages"]
    command = state["command"]
    sql_agent_messages = state["sql_agent_messages"]
    db_agent_feedback = state["db_agent_feedback"]

    # Initialize feedback strings & metadata
    sql_feedback_message = ""
    data_frame_metadata: DataFrameMetadata = {}

    # Create system message
    sys_msg = get_sql_agent_system_message(dialect="SQLite", top_k=5)

    # Determine tool messages after the last AI response
    try:
        last_ai_index = max(
            i for i, msg in enumerate(sql_agent_messages) if msg.type == "ai"
        )
        last_tool_messages = [
            msg
            for msg in sql_agent_messages[last_ai_index + 1:]
            if msg.type == "tool"
        ]
    except:
        st.write("jnnj")
        last_tool_messages = []

    # Process tool messages and gather feedback
    for msg in last_tool_messages:
        if msg.name == "sql_db_query":
            data_frame_metadata = msg.artifact
            sql_feedback_message += f"\n tool output: {msg.content}"
        else:
            st.write(
                "msggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg",
                msg.content,
            )
            sql_feedback_message += f"tool output: {msg.content}\n"

    # Create a context message to pass to the LLM
    context_message = HumanMessage(
        content=f"""
- user query (for context only, do not execute): {query}
- command to execute: {command}

- feedback: {db_agent_feedback} + {sql_feedback_message}    
    """)
    # - feedback: {db_agent_feedback + [sql_feedback_message]}
    # - feedback: {db_agent_feedback} + {sql_feedback_message}
    # - feedback: {format_feedback(db_agent_feedback, sql_feedback_message)}  

    try:
        # Optionally, you could invoke with your full messages list:
        # response = llm_with_tools.invoke([sys_msg] + [command] + sql_agent_messages)
        # Here, it's invoking just sys_msg + context_message:
        response = llm_with_tools.invoke([sys_msg, context_message])

        # Capture the model's response
        feedback_message = f"{response.content}"
        sql_feedback_message += f"{response.content}"

        # If the response includes any tool calls, append them to feedback
        if hasattr(response, "tool_calls") and response.tool_calls:
            for call in response.tool_calls:
                tool_name = call.get("name")
                tool_args = call.get("args", {})

                if tool_name:
                    feedback_message += f"\nCalling the {tool_name} tool"
                    sql_feedback_message += f"\nCalling the {tool_name} tool"
                if tool_args:
                    feedback_message += f" with the following arguments: {tool_args}"
                    sql_feedback_message += f" with the following arguments: {tool_args}"

        # Build the return dictionary
        return_dict = {
            "messages": [response],
            "sql_agent_messages": [response],
            "command": command,
            "feedback": [
                {
                    "agent": "sql_agent",
                    "command": command,
                    "response": feedback_message,
                    "status": "Success",
                }
            ],
            "db_agent_feedback": [sql_feedback_message],
        }

        # Include data_frames_metadata if available
        if data_frame_metadata:
            return_dict["data_frames_metadata"] = [data_frame_metadata]

        return return_dict

    except Exception as e:
        error_msg = HumanMessage(content=str(e))
        return {
            "sql_agent_messages": [error_msg],
            "command": command,
            "feedback": [
                {
                    "status": "error",
                    "step": 2,
                    "message": "SQL execution failed",
                    "result": {
                        "success": False,
                        "data": None,
                        "message": f"Error executing SQL query: {str(e)}",
                        "error": str(e),
                    },
                }
            ],
        }