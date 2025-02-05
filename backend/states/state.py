# states.py

from typing import TypedDict, Annotated, List, Tuple, Union, Optional, Dict
from langchain_core.messages import AnyMessage
import operator
from langgraph.graph import START, StateGraph, END
import json
import pandas as pd


#=================================================Start SQL=================================================#
# class TableSchema(TypedDict):
#     columns: List[str]
#     dtypes: Dict[str, str]
#     description: Optional[str]

# class TableState(TypedDict):
#     data: pd.DataFrame
#     schema: TableSchema
#     comment: Optional[str]
#     last_updated: str  # ISO format timestamp

# class SQLState(TypedDict):
#     tables: Dict[str, TableState]  # Map of table_name to TableState
#     available_tables: List[str]    # List of queryable table names
#     error: Optional[str]





class UnifiedState(TypedDict):
    # messages: Annotated[List[BaseMessage], add]
    voice_query: Optional[bytes]
    query: str
    api_agent_messages: Annotated[list[AnyMessage], operator.add]
    audio_messages: Annotated[List[bytes], operator.add]

    audio_inputs: Optional[bytes]
    audio_outputs: Optional[bytes]
class DataFrameMetadata(TypedDict):
    description: str
    df_id: str
    rows: int
    columns: List[str]
    preview:Dict
    comments: Optional[str]

# class SQLState(TypedDict):
#     tables: Dict[str, TableState]  # Map of table_name to TableState
#     status: Optional[str]
#=================================================End SQL=================================================#
class PlanStep(TypedDict):
  step: int
  action: str
  agent: str


class AnswerState(TypedDict):  
    success: bool  
    response: str  # or Any depending on your response type  
    context: dict  # or specific context structure  
    metadata: dict[str, Union[bool, int, str]]  

class DBAgentResponse(TypedDict):  
    agent: str
    action: str
    response: str  # or Any depending on your response type  
    success: bool

class AgentResponse(TypedDict):  
    agent: str
    action: str
    response: str  # or Any depending on your response type  
    success: bool
class GraphState(TypedDict):
  query: str
#   plan: List[PlanStep]
#   command: str
#   approved: bool  # New field to track approval status
  # current_task: AgentState
#   feedback:Annotated[List[AgentResponse], operator.add]
#   db_agent_feedback:Annotated[List[str], operator.add]
  api_agent_feedback:Annotated[List[str], operator.add]
#   answer:AnswerState
  messages: Annotated[List[AnyMessage], operator.add]
#   sql_agent_messages: Annotated[list[AnyMessage], operator.add]
  api_agent_messages: Annotated[list[AnyMessage], operator.add]
#   data_frames_metadata: Annotated[List[DataFrameMetadata], operator.add]
  # sql_agent_messages: Annotated[List[AnyMessage], operator.add]

class AgentGraphState(TypedDict):
    query: str
    planner_messages: Annotated[list[AnyMessage], operator.add]
    router_messages: Annotated[list[AnyMessage], operator.add]
    sql_agent_messages: Annotated[list[AnyMessage], operator.add]

    messages: Annotated[list[AnyMessage], operator.add]

    # router_response: Annotated[list, add_messages]
    router_response: Annotated[List[Tuple[str, str]], operator.add]
    planner_response: Annotated[List[AnyMessage], operator.add]
    sql_agent_response: Annotated[List[AnyMessage], operator.add]

    final_Answer: Annotated[List[AnyMessage], operator.add]


def where_to_go(state):
  messages = state['messages']
  last_message = messages[-1]

  try:
      # Parse the JSON content
      content = json.loads(last_message.content)

      # Access the status inside the "review" key
      status = content["review"]["status"]

      if "success" in status:
          return END
      elif "failure" in status:
          return "router"
      else:
          return "reviewer error"
  except json.JSONDecodeError:
      # Handle the case where the content is not valid JSON
      return "reviewer error"
  except KeyError:
      # Handle missing keys in the JSON
      return "reviewer error"

# def route(state: dict) -> str:
#   """
#   Routes to the next agent based on the last message in the conversation state.

#   Args:
#       state (dict): Current state containing messages and other information

#   Returns:
#       str: Name of the next agent to execute or 'router_error' if routing fails
#   """
#   try:
#       # Get the last message from the state
#       messages = state.get("messages", [])

#       if not messages:
#           return "planner"  # Default to planner if no messages

#       last_message = messages[-1]

#       # Extract the next_agent from the last message
#       if hasattr(last_message, 'content'):
#           # Handle different message content formats
#           if isinstance(last_message.content, dict):
#               next_agent = last_message.content.get("next_agent", "")
#           elif isinstance(last_message.content, str):
#               # Try to parse JSON if content is string
#               try:
#                   content_dict = json.loads(last_message.content)
#                   next_agent = content_dict.get("next_agent", "")
#               except json.JSONDecodeError:
#                   next_agent = last_message.content
#           else:
#               return "router_error"
#       else:
#           return "router_error"

#       # Route to appropriate agent
#       valid_agents = {
#           "planner": "planner",
#           "web_scraper": "web_scraper",
#           "sql_agent": "sql_agent",
#           "reviewer": "reviewer"
#       }

#       # Check if next_agent matches any valid agent (case insensitive)
#       for agent_key, agent_value in valid_agents.items():
#           if agent_key.lower() in str(next_agent).lower():
#               return agent_value

#       # If no valid agent found
#       return "router_error"

#   except Exception as e:
#       print(f"Routing error: {str(e)}")
#       return "router_error"

import json

def route(state: dict) -> str:
    """
    Routes to the next agent based on the last message in the conversation state.

    Args:
        state (dict): Current state containing messages and other information

    Returns:
        str: Name of the next agent to execute or 'router_error' if routing fails
    """
    try:
        # Get the last message from the state
        messages = state.get("messages", [])

        if not messages:
            return "planner"  # Default to planner if no messages

        last_message = messages[-1]

        # Extract the next_agent from the last message
        next_agent = ""

        if hasattr(last_message, 'content'):
            content = last_message.content

            # Handle different content formats
            if isinstance(content, dict):
                next_agent = content.get("next_agent", "")
            elif isinstance(content, str):
                # Remove code block markers if present
                content = content.strip('`')
                if content.startswith('json\n'):
                    content = content[5:]

                # Try to parse as JSON
                try:
                    content_dict = json.loads(content)
                    next_agent = content_dict.get("next_agent", "")
                except json.JSONDecodeError:
                    next_agent = content
            else:
                return "router_error"
        else:
            return "router_error"

        # Route to appropriate agent
        valid_agents = {
            "planner": "planner",
            "web_scraper": "web_scraper",
            "sql_agent": "sql_agent",
            "reviewer": "reviewer",
            "api_handler": "api_handler"  # Added api_handler
        }

        # Check if next_agent matches any valid agent (case insensitive)
        for agent_key, agent_value in valid_agents.items():
            if agent_key.lower() in str(next_agent).lower():
                return agent_value

        # If no valid agent found
        return "router_error"

    except Exception as e:
        print(f"Routing error: {str(e)}")
        return "router_error"