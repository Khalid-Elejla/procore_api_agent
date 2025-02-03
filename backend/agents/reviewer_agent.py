from ..models.openai_models import load_openai_model  # Import the model loader

# from ..states.state import GraphState, where_to_go
from langchain_core.messages import HumanMessage
from ..prompts.prompts import get_reviewer_system_message
from ..tools.utils_tools import get_search_tool
from ..tools.procore_toolset.users_tools import create_user, get_users
from ..tools.database_tools import sync_users_from_procore

from typing import TypedDict, Annotated, List, Tuple, Dict, Any
import json

import logging

# Define search tool


# Initialize LLM using function from openai_models.py
llm = load_openai_model()

def ReviewerAgent(state: Dict[str, Any]) -> Dict[str, Any]:
  """
  Reviewer agent that synthesizes all previous steps and provides a final response.
  """
  query = state["query"]
  messages = state["messages"]
  plan = state.get("plan", [])
  feedback = state.get("feedback", [])

  # Create a comprehensive context for the reviewer
  context = {
      "original_query": query,
      "execution_plan": plan,
      "execution_feedback": feedback,
      "previous_responses": [msg.content for msg in messages if hasattr(msg, 'content')]
  }

  sys_msg = get_reviewer_system_message()

  # Create a structured prompt that includes all context
  review_prompt = f"""
  Original Query: {context['original_query']}

  Execution Plan:
  {json.dumps(context['execution_plan'], indent=2)}

  Execution Feedback:
  {json.dumps(context['execution_feedback'], indent=2)}

  Please provide a comprehensive response that:
  1. Addresses the original query
  2. Incorporates the execution results
  3. Handles any errors or empty results appropriately
  4. Provides any relevant recommendations or insights
  """


  message = HumanMessage(content=review_prompt)

  try:
      result = llm.invoke([sys_msg, message])

      # Parse the JSON response
      content_dict = json.loads(result.content)


      # Extract only the final_output from the review
      final_output = content_dict["review"]["final_output"]
    #   if not isinstance(final_output, str):
    #       final_output = json.dumps(final_output)


      return {
          "messages": [HumanMessage(content=final_output)],
          "answer": {
              "success": True,
              "response": final_output,
              "context": context,
              "metadata": {
                  "has_sql_results": any(f.get("status") == "success" for f in feedback),
                  "has_errors": any(f.get("status") == "error" for f in feedback),
                  "steps_completed": len(feedback)
              }
          }
      }
  except Exception as e:
      error_response = {
          "messages": [HumanMessage(content=f"Error in review process: {str(e)}")],
          "answer": {
              "success": False,
              "error": str(e),
              "context": context,
              "metadata": {
                  "has_sql_results": False,
                  "has_errors": True,
                  "steps_completed": len(feedback)
              }
          }
      }
      return error_response

