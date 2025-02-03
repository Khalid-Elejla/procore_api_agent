from ..models.openai_models import load_openai_model  # Import the model loader

# from ..states.state import GraphState, where_to_go
from langchain_core.messages import HumanMessage
from ..prompts.prompts import get_reasoner_system_message
from ..tools.utils_tools import get_search_tool
from ..tools.procore_toolset.projects_tools import create_project, get_projects, rename_project
from ..tools.procore_toolset.users_tools import create_user, get_users
from ..tools.database_tools import sync_users_from_procore

# Define search tool
search = get_search_tool()

# Initialize LLM using function from openai_models.py
llm = load_openai_model()
# users_tools=[create_user, get_users]
projects_tools=[create_project, get_projects, rename_project]
database_tools=[sync_users_from_procore]
tools = [search] + database_tools + projects_tools
llm_with_tools = llm.bind_tools(tools)


# Define reasoner function to invoke LLM with the current state
def ReasonerAgent(state):
    query = state["query"]
    messages = state["messages"]
    sys_msg = get_reasoner_system_message()
    message = HumanMessage(content=query)
    messages.append(message)
    result = [llm_with_tools.invoke([sys_msg] + messages)]
    return {"messages": result}