# main.py
from ..models.openai_models import load_openai_model  # Import the model loader
from langgraph.graph import START, StateGraph, END
# from langgraph.prebuilt import tools_condition, ToolNode
from .graph_tools import custom_tools_condition, CustomToolNode

from IPython.display import Image, display

from ..states.state import  route, GraphState, where_to_go, UnifiedState
from langchain_core.messages import HumanMessage, BaseMessage
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
# logging.basicConfig(level=logging.INFO)
from langgraph.checkpoint.memory import MemorySaver # Human in the loop

from ..utils.audio_utils import record_audio_until_stop, play_audio


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

        # df_manager = DataFrameManager()

        logging.info(f"I am here: 60")
        # Initialize LLM using function from openai_models.py
        llm = load_openai_model()
        api_spec_file = 'OAS_updated.json'
        base_url = "https://sandbox.procore.com"
        overrides = {"servers": [{"url": base_url}]}

        if 'access_token' not in st.session_state:
            st.session_state.access_token = None
        access_token = st.session_state.access_token

        load_dotenv()
        company_id=os.getenv("PROCORE_COMPANY_ID")
        logging.info(f"Final database tools: {company_id}")

        # database_tools = initialize_db_tools(db_uri="sqlite:///backend\\procore_db.sqlite", df_manager= df_manager)
        api_tools = initialize_api_tools(company_id, access_token, api_spec_file, overrides)

        builder = StateGraph(GraphState)



        # builder.add_node("planner", PlannerAgent)
        # builder.add_node("router", RouterAgent)
        # builder.add_node("sql_agent", SQLAgent)
        # builder.add_node("reviewer", ReviewerAgent)
        builder.add_node("api_handler", APIHandlerAgent)
        builder.add_node("api_tools", CustomToolNode(api_tools, message_key="api_agent_messages"))


        # builder.add_node("sql_tools", CustomToolNode(database_tools, message_key="sql_agent_messages"))

        builder.add_edge(START, "api_handler")



        # builder.add_edge(START, "planner")
        # builder.add_edge("planner", "router")

        # builder.add_conditional_edges("router", route)


        # builder.add_conditional_edges(
        #     "sql_agent",
        #     lambda state: custom_tools_condition(state, message_key="sql_agent_messages"),  {
        #         "tools": "sql_tools",
        #         "__end__": "router"
        #     }
        # )

        builder.add_conditional_edges(
            "api_handler",
            lambda state: custom_tools_condition(state, message_key="api_agent_messages"),  {
                "tools": "api_tools",
                "__end__": END
            }
        )

        # builder.add_edge("sql_tools", "sql_agent")
        builder.add_edge("api_tools", "api_handler")

        # builder.add_edge("reviewer", END)
        # builder.add_edge("api_handler", END)

#================================================================================================
        # Human in the loop
        checkpointer = MemorySaver()
        # sub_graph = builder.compile(checkpointer=checkpointer)



        # def call_subgraph(state: State):
        #     return react_graphs.invoke({"subgraph_key": state["parent_key"]})


        from typing import Annotated, Optional, List
        from typing_extensions import TypedDict
        from operator import add


            
        main_builder = StateGraph(UnifiedState)
        # Add audio input and output nodes
        main_builder.add_node("subgraph", builder.compile())
        main_builder.add_node("audio_input", record_audio_until_stop)
        main_builder.add_node("audio_output", play_audio)

        # Connect the nodes
        main_builder.add_edge(START, "audio_input")
        main_builder.add_edge("audio_input", "subgraph")
        main_builder.add_edge("subgraph", "audio_output")
        main_builder.add_edge("audio_output", END)



        react_graphs = main_builder.compile(checkpointer=checkpointer)
#================================================================================================
        # react_graphs = builder.compile()

        logging.info("Graph built successfully!")
        return react_graphs
    except Exception as e:
        logging.error(f"Error occurred in build_graph: {e}")
        raise RuntimeError("Graph building failed") from e 
