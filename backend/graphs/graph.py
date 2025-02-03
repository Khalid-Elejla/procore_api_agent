# main.py
from ..models.openai_models import load_openai_model  # Import the model loader
from langgraph.graph import START, StateGraph, END
# from langgraph.prebuilt import tools_condition, ToolNode
from .graph_tools import custom_tools_condition, CustomToolNode

from IPython.display import Image, display

from ..states.state import  route, GraphState, where_to_go
from langchain_core.messages import HumanMessage
# from ..prompts.prompts import get_reasoner_system_message
from ..tools.utils_tools import get_search_tool
from ..tools.procore_toolset.projects_tools import create_project, get_projects, rename_project
from ..tools.procore_toolset.users_tools import create_user, get_users
from ..tools.database_tools import sync_users_from_procore
# from ..agents.reasoner_agent import ReasonerAgent
from ..agents.planner_agent import PlannerAgent
from ..agents.router_agent import RouterAgent
from ..agents.sql_agent import SQLAgent
from ..agents.reviewer_agent import ReviewerAgent
from ..agents.api_handler_agent import APIHandlerAgent

from langchain_community.utilities import SQLDatabase
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from ..tools.database_toolkit import CustomSQLDatabaseToolkit

from ..tools.dataframe_manager import DataFrameManager
import streamlit as st
from ..tools.initialize_tools import initialize_db_tools, initialize_api_tools
import os
from dotenv import load_dotenv

import logging
logging.basicConfig(level=logging.INFO)
from langgraph.checkpoint.memory import MemorySaver # Human in the loop


def build_graph():
    try:

        # llm = load_openai_model()
        # df_manager = DataFrameManager()
        # # logging.debug("Initializing SQLDatabaseToolkit...")
        # db_uri = "sqlite:///backend\\procore_db.sqlite"
        # # toolkit = SQLDatabaseToolkit(db=db, llm=load_openai_model(temperature=0))
        
        # toolkit = CustomSQLDatabaseToolkit(db=db, llm=load_openai_model(temperature=0), tools_kwargs={"df_manager": df_manager})

        # # logging.debug("Fetching tools from toolkit...")
        # langchain_sql_toolbox = toolkit.get_tools()
        # # logging.debug(f"Tools fetched: {langchain_sql_toolbox}")

        # # database_tools = [sync_users_from_procore] + langchain_sql_toolbox
        # database_tools = toolkit.get_tools()

        df_manager = DataFrameManager()


        # Initialize LLM using function from openai_models.py
        llm = load_openai_model()
        api_spec_file = 'OAS.json'
        base_url = "https://sandbox.procore.com"
        overrides = {"servers": [{"url": base_url}]}

        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        access_token = st.session_state.access_token
        
        load_dotenv()
        company_id=os.getenv("PROCORE_COMPANY_ID")
        logging.info(f"Final database tools: {company_id}")

        database_tools = initialize_db_tools(db_uri="sqlite:///backend\\procore_db.sqlite", df_manager= df_manager)
        api_tools = initialize_api_tools(company_id, access_token, api_spec_file, overrides)
        logging.info(f"Final database tools: {api_tools}")
        builders = StateGraph(GraphState)

        

        builders.add_node("planner", PlannerAgent)
        builders.add_node("router", RouterAgent)
        builders.add_node("sql_agent", SQLAgent)
        builders.add_node("reviewer", ReviewerAgent)
        builders.add_node("api_handler", APIHandlerAgent)
        builders.add_node("api_tools", CustomToolNode(api_tools, message_key="api_agent_messages"))
        builders.add_node("sql_tools", CustomToolNode(database_tools, message_key="sql_agent_messages"))

        builders.add_edge(START, "planner")
        builders.add_edge("planner", "router")

        builders.add_conditional_edges("router", route)

        # builders.add_conditional_edges(
        #     "sql_agent",
        #     tools_condition,
        #     {
        #         "tools": "sql_tools",
        #         "__end__": "router"
        #     }
        # )

        builders.add_conditional_edges(
            "sql_agent",
            lambda state: custom_tools_condition(state, message_key="sql_agent_messages"),  {
                "tools": "sql_tools",
                "__end__": "router"
            }
        )

        builders.add_conditional_edges(
            "api_handler",
            lambda state: custom_tools_condition(state, message_key="api_agent_messages"),  {
                "tools": "api_tools",
                "__end__": "router"
            }
        )

        builders.add_edge("sql_tools", "sql_agent")
        builders.add_edge("api_tools", "api_handler")
   
        builders.add_edge("reviewer", END)


#================================================================================================
        # Human in the loop
        checkpointer = MemorySaver()
        react_graphs = builders.compile(checkpointer=checkpointer)
#================================================================================================
        # react_graphs = builders.compile()

        # logging.debug("Graph built successfully!")
        return react_graphs
    except Exception as e:
        # logging.error(f"Error occurred in build_graph: {e}")
        raise
