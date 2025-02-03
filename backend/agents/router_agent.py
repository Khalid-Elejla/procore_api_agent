from ..models.openai_models import load_openai_model  # Import the model loader

# from ..states.state import GraphState, where_to_go
from langchain_core.messages import HumanMessage
from ..prompts.prompts import get_router_system_message
from ..tools.utils_tools import get_search_tool
from ..tools.procore_toolset.projects_tools import create_project, get_projects, rename_project
from ..tools.procore_toolset.users_tools import create_user, get_users
from ..tools.database_tools import sync_users_from_procore

from typing import Dict, Any
import json
import logging

# Define search tool
search = get_search_tool()

# Initialize LLM using function from openai_models.py
llm = load_openai_model()
# users_tools=[create_user, get_users]
# projects_tools=[create_project, get_projects, rename_project]
# database_tools=[sync_users_from_procore]
# tools = [search] + database_tools + projects_tools
# llm_with_tools = llm.bind_tools(tools)



def RouterAgent(state: Dict[str, Any]) -> Dict[str, Any]:
  """
  Router agent that determines the next agent to handle the conversation.

  Args:
      state (Dict[str, Any]): Contains query, messages, plan, and feedback

  Returns:
      Dict[str, Any]: Contains updated messages and routing information
  """
  query = state["query"]
  messages = state["messages"]
#   logging.error("leeeeeeeeeeeeeeennnnnnnnn messages", len(messages))
  # Handle the plan from PlannerAgent
  if isinstance(state.get("plan"), list):
      plan = json.dumps(state["plan"], indent=2)
  else:
      plan = state.get("plan", "No plan available yet")

  feedback = state.get("feedback", "No feedback available yet")

  # Get system message with plan and feedback
  # sys_msg = get_router_system_message(plan=plan, feedback=feedback)

  sys_msg = get_router_system_message()

  # Create a structured prompt that includes all context
  router_prompt = f"""
  here is the user original query
  query: {query}

  Here is the plan provided by the planner:
  Plan: {plan}

  Here is the feedback provided by the agents:
  Feedback: {feedback}
  """
  message = HumanMessage(content=router_prompt)

#33

  # Add user query to messages
#   message = HumanMessage(content=query)
#   messages.append(message)

  # Get LLM response
  # response = llm.invoke([sys_msg] + messages)
  # response = llm.invoke([sys_msg] + messages)
  response = llm.invoke([sys_msg, message])

#   messages.append(response)


  # Parse the JSON response
  try:
      
      response.content = response.content.strip('`')
      if response.content.startswith('json\n'):
          response.content = response.content[5:]

      routing_decision = json.loads(response.content)
      next_agent= routing_decision["next_agent"]
      command= routing_decision["command"]
      return {
          # "messages": messages,
          "messages": [response],

        #   "next_agent": routing_decision["next_agent"],
          "next_agent": next_agent,
          "command": command,
          "feedback": [{
                  "agent": "router",
                  "action": "Route the request to the most appropriate agent.",
                  "response": f"routing to {next_agent} to execute: {command}",
                  "status": "Success"
              }]
      }

  except json.JSONDecodeError:
      # Fallback if response is not valid JSON
      return {
          # "messages": messages,
          "messages": [response],
          "next_agent": "planner",  # Default to planner if parsing fails
          "command": "Please provide a clear plan for the task",
          "feedback":[ {
              "agent": "router",
              "action": "Route the request to the most appropriate agent.",
              "response": "routing to planner agent to provide a clear plan for the task",
              "status": "Error"
              }]
      }