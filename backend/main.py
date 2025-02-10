# import os
# import base64
# from dotenv import load_dotenv

# import logging
# import traceback


# load_dotenv()

# from .utils.helper_functions import get_langfuse_handler #, suppress_print
# from .graphs.graph import build_graph

# # Main execution
# # def run_agent_graph(query: str) -> str:
# def run_agent_graph(query, query_type="text"):
#   # query = "give more information about Grashavyr Boogodyr"
  
#   # Initialize Langfuse handler (assuming you are storing the keys in .env)
#   langfuse_handler = get_langfuse_handler()

#   # Build the state graph
#   assistant_graph = build_graph(query_type)
  
#   access_token = os.getenv('access_token')
#   company_id = os.getenv('PROCORE_COMPANY_ID')

# #================================================================================================



#   try:
#     if query_type=="text":
#       # Convert bytes to Base64 string
#       result = assistant_graph.invoke({"query": query, "messages": []}, config={"callbacks": [langfuse_handler],"thread_id": "1",})
#     elif query_type=="voice":
#             # Convert bytes to Base64 string
#       query = base64.b64encode(query).decode('utf-8')
#       result = assistant_graph.invoke({"voice_query": query, "messages": []}, config={"callbacks": [langfuse_handler],"thread_id": "1",})

#   except Exception as e:
#     # logging.error(f"query: {query}")
#     logging.error(f"query type: {type(query)}")

#     logging.error(f"Error occurred in build_graph: {e}")
#     logging.error(f"Traceback details:\n {traceback.format_exc()}")


# #   try:
# #     result = assistant_graph.invoke({"query": query, "messages": []}, config={"callbacks": [langfuse_handler],"thread_id": "1"})
# #   except Exception as e:
# #     result = assistant_graph.invoke(Command(resume={"run_api_call":"yes"}), config={"callbacks": [langfuse_handler],"thread_id": "1"},)
# # #================================================================================================

#   # result = assistant_graph.invoke({"query": query, "messages": []}, config={"callbacks": [langfuse_handler]})

#   # with suppress_print():      
#   #     result = assistant_graph.invoke({"query": query, "messages": []}, config={"callbacks": [langfuse_handler]})

#   # # Display the result
#   # result['messages'][-1].pretty_print()
#   answer=result['messages'][-1]
#   logging.info(f"here is the assistant answer: {answer}")
#   return answer

# if __name__ == "__main__":
#     run_agent_graph()

#============================================================================================================================
# import os
# import base64
# import logging
# import traceback
# from dotenv import load_dotenv
# from .utils.helper_functions import get_langfuse_handler
# from .graphs.graph import build_graph

# load_dotenv()

# logger = logging.getLogger(__name__)

# def run_agent_graph(query: str | bytes, query_type: str = "text") -> str:
#     """Execute the agent graph based on query type."""
#     langfuse_handler = get_langfuse_handler()
#     assistant_graph = build_graph(query_type)
#     config = {"callbacks": [langfuse_handler], "thread_id": "1"}

#     try:
#         if query_type == "voice":
#             query = base64.b64encode(query).decode('utf-8')
#             input_data = {"voice_query": query, "messages": []}
#         else:
#             input_data = {"query": query, "messages": []}

#         result = assistant_graph.invoke(input_data, config=config)
#         answer = result['messages'][-1]
        
#         logger.info(f"Assistant answer: {answer}")
#         return answer

#     except Exception as e:
#         logger.error(
#             f"Error processing {query_type} query (type: {type(query)}): {e}\n"
#             f"Traceback:\n{traceback.format_exc()}"
#         )
#         raise  # Consider re-raising or handling error appropriately

# if __name__ == "__main__":
#     run_agent_graph()
#============================================================================================================================
#main.py
import os
import base64
import logging
import traceback
from dotenv import load_dotenv
from .utils.helper_functions import get_langfuse_handler
from .graphs.graph import build_graph

load_dotenv()

logger = logging.getLogger(__name__)

class AgentGraphManager:
    def __init__(self):
        self.text_graph = None
        self.voice_graph = None
        self.langfuse_handler = get_langfuse_handler()

    def get_graph(self, query_type: str):
        if query_type == "voice":
            if self.voice_graph is None:
                self.voice_graph = build_graph("voice")
            return self.voice_graph
        else:
            if self.text_graph is None:
                self.text_graph = build_graph("text")
            return self.text_graph

# Create a singleton instance
graph_manager = AgentGraphManager()

def run_agent_graph(query: str | bytes, query_type: str = "text") -> str:
    """Execute the agent graph based on query type."""
    # config = {"callbacks": [graph_manager.langfuse_handler], "thread_id": "1"}

    # Conditionally include langfuse handler only for text queries
    config = {
        "callbacks": [graph_manager.langfuse_handler] if query_type == "text" else [],
        "thread_id": "2"
    }

    try:
        if query_type == "voice":
            query = base64.b64encode(query).decode('utf-8')
            # input_data = {"voice_query": query, "messages": []}
            input_data = {"voice_query": query}

        else:
            # input_data = {"query": query, "messages": []}
            input_data = {"query": query}


        assistant_graph = graph_manager.get_graph(query_type)
        result = assistant_graph.invoke(input_data, config=config)
        answer = result['messages'][-1].content

        logger.info(f"Assistant answer: {answer}")
        return answer

    except Exception as e:
        logger.error(
            f"Error processing {query_type} query (type: {type(query)}): {e}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        raise

if __name__ == "__main__":
    run_agent_graph()