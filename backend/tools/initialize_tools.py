import logging
from ..models.openai_models import load_openai_model 
from langchain_community.utilities import SQLDatabase
from .dataframe_manager import DataFrameManager
from .database_toolkit import CustomSQLDatabaseToolkit
#================================================================================================
from .procore_api_tools import HTTPRequestTool
from .procore_api_tools import EndpointEmbeddingManager
# from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec
from ..utils.helper_functions import enhanced_reduce_openapi_spec
import yaml
import streamlit as st
import os
import json
from typing import List
import logging

# Load the API specification from a YAML file
def load_reduced_api_spec(file_path: str, overrides: dict = None) -> dict:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")
    
    with open(file_path, "r") as file:
        if file_path.endswith(".yaml") or file_path.endswith(".yml"):
            api_spec = yaml.load(file, Loader=yaml.Loader)
        elif file_path.endswith(".json"):
            api_spec = json.load(file)
        else:
            raise ValueError("Unsupported file format. Please provide a .yaml, .yml, or .json file.")

    # Apply modifications if provided
    if overrides:
        for key, value in overrides.items():
            api_spec[key] = value
                
    # Reduce the OpenAPI specification for use
#    reduced_api_spec = reduce_openapi_spec(api_spec)
    reduced_api_spec = enhanced_reduce_openapi_spec(api_spec, latest_version_only=True)

    return reduced_api_spec


def initialize_api_tools(
    company_id: str = None,
    access_token : str = None,
    api_spec_file: str = None,
    overrides: dict = None, 
):
    headers= {"Authorization": f"Bearer {access_token}","Procore-Company-Id":f"{company_id}"}
    http_tool = HTTPRequestTool(headers = headers)
    

    
    # class BertEmbeddings:
    #     def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
    #         self.model = SentenceTransformer(model_name)

    #     def embed_documents(self, texts: List[str]) -> List[List[float]]:
    #         return self.model.encode(texts, convert_to_numpy=True)

    #     def embed_query(self, text: str) -> List[float]:
    #         return self.model.encode(text, convert_to_numpy=True)
    
    # bert_embeddings = BertEmbeddings()
    # endpoints_manager = EndpointEmbeddingManager(embedding_model=bert_embeddings)
    endpoints_manager = EndpointEmbeddingManager()



    
    try:
        # endpoints_manager.load_embeddings('endpoint_embeddings.pkl')
        endpoints_manager.load_embeddings('new_endpoint_embeddings2.pkl')
    except FileNotFoundError:
        # Initial embedding creation
        # overrides = {"servers": [{"url": "https://sandbox.procore.com"}]}
        reduced_api_spec = load_reduced_api_spec(api_spec_file, overrides)
        endpoints = reduced_api_spec.endpoints # Your list of endpoints
        endpoints_manager.embed_endpoints(endpoints)
        endpoints_manager.save_embeddings('new_endpoint_embeddings2.pkl')
        #endpoints_manager.load_embeddings('endpoint_embeddings.pkl')

    try:
        api_toolbox=[http_tool._run, endpoints_manager.find_relevant_endpoints]
        return api_toolbox
    except Exception as e:
        logging.error(f"Error initializing tools: {e}")
        return None


def initialize_db_tools(
    db_uri: str,  # Default database URI
    model_name: str = "gpt-4o-mini",  # Default model name
    temperature: float = 0.0,  # Default temperature for the model
    df_manager: DataFrameManager = None,  # Optional, default to None if no custom manager is provided
):
    """
    Initializes the SQL database toolkit and retrieves tools for interaction.
    This function sets up the OpenAI model, dataframe manager, and connects
    to the SQL database before fetching the tools needed for operations.
    
    Args:
        model_name (str): The name of the OpenAI model to load.
        temperature (float): The temperature setting for the OpenAI model.
        db_uri (str): URI for connecting to the SQL database.
        df_manager (DataFrameManager): Optional custom dataframe manager; if None, a default will be used.
    
    Returns:
        list: A list of database tools from the custom toolkit, or None if an error occurs.
    """
    try:
        # Initialize the LLM (Language Learning Model) with the specified model name
        llm = load_openai_model(model=model_name, temperature=temperature)

        # Use provided DataFrame Manager or initialize a default one
        df_manager = df_manager if df_manager else DataFrameManager()

        # Initialize the SQL database connection using the provided URI
        db = SQLDatabase.from_uri(db_uri)

        # Set up the custom toolkit with the SQL database, LLM, and DataFrame manager
        toolkit = CustomSQLDatabaseToolkit(
            db=db, 
            llm=llm,
            tools_kwargs={"df_manager": df_manager}  # Pass DataFrame manager as a tool argument
        )
        # logging.error(f"Error initializing tools: {toolkit}")
        # Fetch the tools from the custom toolkit
        sql_toolbox = toolkit.get_tools(df_manager)

        # # Return the set of tools that can be used for database operations
        # logging.debug("Tools successfully initialized.")
        
        return sql_toolbox

    except Exception as e:
        # logging.error(f"Error initializing tools: {e}")
        return None
