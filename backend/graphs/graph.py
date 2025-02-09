# # main.py
# from ..models.openai_models import load_openai_model  # Import the model loader
# from langgraph.graph import START, StateGraph, END
# # from langgraph.prebuilt import tools_condition, ToolNode
# from .graph_tools import custom_tools_condition, CustomToolNode

# from IPython.display import Image, display

# from ..states.state import  route, GraphState, where_to_go, UnifiedState
# from langchain_core.messages import HumanMessage, BaseMessage
# # from ..prompts.prompts import get_reasoner_system_message
# from ..tools.utils_tools import get_search_tool
# from ..tools.procore_toolset.projects_tools import create_project, get_projects, rename_project
# from ..tools.procore_toolset.users_tools import create_user, get_users
# from ..tools.database_tools import sync_users_from_procore
# # from ..agents.reasoner_agent import ReasonerAgent
# from ..agents.planner_agent import PlannerAgent
# from ..agents.router_agent import RouterAgent
# from ..agents.sql_agent import SQLAgent
# from ..agents.reviewer_agent import ReviewerAgent
# from ..agents.api_handler_agent import APIHandlerAgent

# from langchain_community.utilities import SQLDatabase
# # from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
# from ..tools.database_toolkit import CustomSQLDatabaseToolkit

# from ..tools.dataframe_manager import DataFrameManager
# import streamlit as st
# from ..tools.initialize_tools import initialize_db_tools, initialize_api_tools
# import os
# from dotenv import load_dotenv

# import logging
# # logging.basicConfig(level=logging.INFO)
# from langgraph.checkpoint.memory import MemorySaver # Human in the loop

# from ..utils.audio_utils import record_audio_until_stop, play_audio


# def build_graph():
#     try:

#         # llm = load_openai_model()
#         # df_manager = DataFrameManager()
#         # # logging.debug("Initializing SQLDatabaseToolkit...")
#         # db_uri = "sqlite:///backend\\procore_db.sqlite"
#         # # toolkit = SQLDatabaseToolkit(db=db, llm=load_openai_model(temperature=0))

#         # toolkit = CustomSQLDatabaseToolkit(db=db, llm=load_openai_model(temperature=0), tools_kwargs={"df_manager": df_manager})

#         # # logging.debug("Fetching tools from toolkit...")
#         # langchain_sql_toolbox = toolkit.get_tools()
#         # # logging.debug(f"Tools fetched: {langchain_sql_toolbox}")

#         # # database_tools = [sync_users_from_procore] + langchain_sql_toolbox
#         # database_tools = toolkit.get_tools()

#         # df_manager = DataFrameManager()

#         logging.info(f"I am here: 60")
#         # Initialize LLM using function from openai_models.py
#         llm = load_openai_model()
#         api_spec_file = 'OAS_updated.json'
#         base_url = "https://sandbox.procore.com"
#         overrides = {"servers": [{"url": base_url}]}

#         if 'access_token' not in st.session_state:
#             st.session_state.access_token = None
#         access_token = st.session_state.access_token

#         load_dotenv()
#         company_id=os.getenv("PROCORE_COMPANY_ID")
#         logging.info(f"Final database tools: {company_id}")

#         # database_tools = initialize_db_tools(db_uri="sqlite:///backend\\procore_db.sqlite", df_manager= df_manager)
#         api_tools = initialize_api_tools(company_id, access_token, api_spec_file, overrides)

#         builder = StateGraph(GraphState)



#         # builder.add_node("planner", PlannerAgent)
#         # builder.add_node("router", RouterAgent)
#         # builder.add_node("sql_agent", SQLAgent)
#         # builder.add_node("reviewer", ReviewerAgent)
#         builder.add_node("api_handler", APIHandlerAgent)
#         builder.add_node("api_tools", CustomToolNode(api_tools, message_key="api_agent_messages"))


#         # builder.add_node("sql_tools", CustomToolNode(database_tools, message_key="sql_agent_messages"))

#         builder.add_edge(START, "api_handler")



#         # builder.add_edge(START, "planner")
#         # builder.add_edge("planner", "router")

#         # builder.add_conditional_edges("router", route)


#         # builder.add_conditional_edges(
#         #     "sql_agent",
#         #     lambda state: custom_tools_condition(state, message_key="sql_agent_messages"),  {
#         #         "tools": "sql_tools",
#         #         "__end__": "router"
#         #     }
#         # )

#         builder.add_conditional_edges(
#             "api_handler",
#             lambda state: custom_tools_condition(state, message_key="api_agent_messages"),  {
#                 "tools": "api_tools",
#                 "__end__": END
#             }
#         )

#         # builder.add_edge("sql_tools", "sql_agent")
#         builder.add_edge("api_tools", "api_handler")

#         # builder.add_edge("reviewer", END)
#         # builder.add_edge("api_handler", END)

# #================================================================================================
#         # Human in the loop
#         checkpointer = MemorySaver()
#         # sub_graph = builder.compile(checkpointer=checkpointer)



#         # def call_subgraph(state: State):
#         #     return react_graphs.invoke({"subgraph_key": state["parent_key"]})


#         from typing import Annotated, Optional, List
#         from typing_extensions import TypedDict
#         from operator import add


            
#         main_builder = StateGraph(UnifiedState)
#         # Add audio input and output nodes
#         main_builder.add_node("subgraph", builder.compile())
#         main_builder.add_node("audio_input", record_audio_until_stop)
#         main_builder.add_node("audio_output", play_audio)

#         # Connect the nodes
#         main_builder.add_edge(START, "audio_input")
#         main_builder.add_edge("audio_input", "subgraph")
#         main_builder.add_edge("subgraph", "audio_output")
#         main_builder.add_edge("audio_output", END)



#         react_graphs = main_builder.compile(checkpointer=checkpointer)
# #================================================================================================
#         # react_graphs = builder.compile()

#         logging.info("Graph built successfully!")
#         return react_graphs
#     except Exception as e:
#         logging.error(f"Error occurred in build_graph: {e}")
#         raise RuntimeError("Graph building failed") from e 
#====================================================================================================================================

# main.py
import os
import logging
from typing import Optional
from dotenv import load_dotenv
import streamlit as st

from langgraph.graph import START, StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from ..models.openai_models import load_openai_model
from ..states.state import GraphState, UnifiedState
from ..tools.initialize_tools import initialize_api_tools
from ..utils.audio_utils import record_audio_until_stop, play_audio
from .graph_tools import custom_tools_condition, CustomToolNode
from ..agents.api_handler_agent import APIHandlerAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def initialize_environment():
    """Initialize shared environment variables and configurations"""
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
        
    return {
        'access_token': st.session_state.access_token,
        'company_id': os.getenv("PROCORE_COMPANY_ID"),
        'api_spec_file': os.getenv("PROCORE_API_SPEC_FILE"),
        'base_url': os.getenv("PROCORE_API_BASE_URL"),
        'OPENAI_API_KEY': os.getenv("OPENAI_API_KEY")
    }

def create_api_tools(config: dict):
    """Initialize and return API tools"""
    return initialize_api_tools(
        company_id=config['company_id'],
        access_token=config['access_token'],
        api_spec_file=config['api_spec_file'],
        overrides={"servers": [{"url": config['base_url']}]}
    )

def build_base_graph() -> StateGraph:
    """Build and return the core state graph"""
    builder = StateGraph(GraphState)
    
    # Add nodes
    api_tools = CustomToolNode(
        create_api_tools(initialize_environment()), 
        message_key="api_agent_messages"
    )
    
    builder.add_node("api_handler", APIHandlerAgent)
    builder.add_node("api_tools", api_tools)

    # Set up edges
    builder.add_edge(START, "api_handler")
    builder.add_edge("api_tools", "api_handler")

    builder.add_conditional_edges(
        "api_handler",
        lambda state: custom_tools_condition(state, message_key="api_agent_messages"),
        {"tools": "api_tools", "__end__": END}
    )

    return builder.compile()

def build_voice_enabled_graph(base_graph: StateGraph) -> StateGraph:
    """Wrap base graph with audio processing nodes"""
    main_builder = StateGraph(UnifiedState)
    checkpointer = MemorySaver()

    # Add audio processing nodes
    main_builder.add_node("subgraph", base_graph)
    main_builder.add_node("audio_input", record_audio_until_stop)
    main_builder.add_node("audio_output", play_audio)

    # Connect nodes
    main_builder.add_edge(START, "audio_input")
    main_builder.add_edge("audio_input", "subgraph")
    main_builder.add_edge("subgraph", "audio_output")
    main_builder.add_edge("audio_output", END)

    return main_builder.compile(checkpointer=checkpointer)

def build_graph(query_type = "text"):
    """Main function to build and return the complete graph"""
    try:
        logger.info("Initializing graph components...")
        
        # Load environment variables
        load_dotenv()
        # OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

        # Initialize core components
        load_openai_model()  # Ensure model is loaded
        if query_type == "text":
            base_graph = build_base_graph()
            graph = base_graph
            # graph = base_graph.compile()  # Compile the graph
        elif query_type == "voice":
            base_graph = build_base_graph()
            voice_enabled_graph = build_voice_enabled_graph(base_graph)
            graph= voice_enabled_graph

        logger.info("Graph built successfully!")


        return graph
    
    except Exception as e:
        logger.error(f"Graph construction failed: {str(e)}", exc_info=True)
        raise RuntimeError(f"Graph building failed: {str(e)}") from e