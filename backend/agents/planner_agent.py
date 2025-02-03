from ..models.openai_models import load_openai_model  # Import the model loader

# from ..states.state import GraphState, where_to_go
from langchain_core.messages import HumanMessage, AIMessage
from ..prompts.prompts import get_planner_system_message
from ..tools.utils_tools import get_search_tool
from ..tools.procore_toolset.projects_tools import create_project, get_projects, rename_project
from ..tools.procore_toolset.users_tools import create_user, get_users
from ..tools.database_tools import sync_users_from_procore

import json
from typing import Dict, Any
import logging

# Define search tool
# search = get_search_tool()

# Initialize LLM using function from openai_models.py
llm = load_openai_model()
# users_tools=[create_user, get_users]
# projects_tools=[create_project, get_projects, rename_project]
# database_tools=[sync_users_from_procore]
# tools = [search] + database_tools + projects_tools
# llm_with_tools = llm.bind_tools(tools)


# # Define reasoner function to invoke LLM with the current state
# def PlannerAgent(state):
#     query = state["query"]
#     messages = state["messages"]
#     sys_msg = get_planner_system_message()
#     message = HumanMessage(content=query)
#     messages.append(message)
# #    result = [llm_with_tools.invoke([sys_msg] + messages)]
#     plan = llm.invoke([sys_msg] + messages)
#     result=[plan]
#     # return {"messages": result}
#     return {"plan": plan.content}#,"messages": result}

def PlannerAgent(state: Dict[str, Any]) -> Dict[str, Any]:
    query = state["query"]
    messages = state["messages"]

    sys_msg = get_planner_system_message()
    message = HumanMessage(content=query)
    messages.append(message)


    # plan = llm.invoke([sys_msg] + messages)
    plan = llm.invoke([sys_msg] + messages)
    messages.append(plan)

    try:
        plan_dict = json.loads(plan.content)
        # Validate the plan structure
        for step in plan_dict["plan"]:
            assert isinstance(step, dict)
            assert all(k in step for k in ["step", "action", "agent"])

        return {
            "plan": plan_dict["plan"],
            "feedback": [{
                  "agent": "planner",
                  "action": "Generate a plan to address the user's request.",
                  "response": f"The plan was successfully generated.",
                  "status": "Success"
              }]
            #"messages": messages
            # "messages": messages + [plan],
            # "messages": [plan],

        }
    except (json.JSONDecodeError, AssertionError) as e:
        # logging.error(f"Plan generation error: {e}")
        # logging.error(f"Raw response: {plan.content}")
        return {
            "plan": [{"step": 1, "action": "Error in plan generation. Please refine your query.", "agent": "planner"}],
            "feedback": [{
                  "agent": "planner",
                  "action": "Generate a plan to address the user's request.",
                  "response": f"Error in plan generation. Please refine your query.",
                  "status": "Error"
              }]
            #"messages": messages
            # "messages": messages + [plan],
            # "messages": [plan],
        }


#   try:
#       # Parse the plan content as JSON
#       plan_dict = json.loads(plan.content)
#       return {
#           "plan": plan_dict["plan"],
#           "messages": messages + [plan],
#         #   "messages":[plan],
#           # "feedback":[AIMessage(content=json.dumps(step)) for step in plan]
#       }
#   except json.JSONDecodeError as e:
#       logging.error(f"JSON parsing failed. Raw content: {plan.content}")
#       logging.error(e)
#       # Fallback if parsing fails
#       return {
#           "plan": [{"step": 1, "action": "Error in plan generation", "agent": "planner"}],
#           "messages": messages + [plan],
#         #  "messages": [plan],
#           # "feedback":[AIMessage(content=json.dumps(step)) for step in plan]
#       }