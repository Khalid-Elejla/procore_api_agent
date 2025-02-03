# from typing import Optional, Dict, Any, Literal, List
# from pydantic import BaseModel, Field
# import requests
# import re

# from langchain_core.embeddings import Embeddings
# from langchain_openai import OpenAIEmbeddings
# import numpy as np
# import json
# import pickle
# from typing import List, Tuple, Dict
# import faiss
# from langgraph.types import Command
# from langchain_core.messages import ToolMessage


# class HTTPResponse(BaseModel):
#     """Model for HTTP responses"""
#     status_code: int
#     content: str
#     headers: Dict[str, str]

# class PathParameter(BaseModel):
#     """Model for path parameters"""
#     name: str
#     description: str
#     required: bool = True
#     example: str = ""

# class RequestBodySchema(BaseModel):
#     """Model for request body schema"""
#     type: str
#     example: Dict[str, Any] = Field(default_factory=dict)

# class APIEndpoint(BaseModel):
#     """Model for API endpoint documentation"""
#     method: str
#     path: str
#     description: str
#     path_parameters: List[PathParameter] = Field(default_factory=list)
#     request_body: Optional[RequestBodySchema] = None

# class HTTPRequestTool(BaseModel):
#     """Generic tool for making HTTP requests"""
#     name: str = "http_request"
#     description: str = """Make HTTP requests to API endpoints. Handles path parameters, query parameters, and request body.
#     Required inputs:
#     - method: HTTP method (GET, POST, PUT, DELETE, PATCH)
#     - base_url: Base URL of the API
#     - endpoint: API endpoint path (with path parameters in {param_name} format)
#     Optional inputs:
#     - path_params: Dictionary of path parameters to replace in the endpoint
#     - query_params: Dictionary of query parameters
#     - headers: Dictionary of request headers
#     - body: Dictionary for request body (for POST/PUT/PATCH)
#     """
#     allow_dangerous_requests: bool = False
#     headers: Dict[str, str] = Field(default_factory=dict) 

#     class Config:
#         arbitrary_types_allowed = True

#     def _replace_path_parameters(self, endpoint: str, path_params: Dict[str, Any]) -> str:
#         """Replace path parameters in endpoint URL"""
#         for param_name, param_value in path_params.items():
#             pattern = f"{{{param_name}}}"
#             endpoint = endpoint.replace(pattern, str(param_value))
#         return endpoint

#     def _make_request(
#         self,
#         method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
#         base_url: str,
#         endpoint: str,
#         path_params: Optional[Dict[str, Any]] = None,
#         query_params: Optional[Dict[str, Any]] = None,
#         headers: Optional[Dict[str, str]] = None,
#         body: Optional[Dict[str, Any]] = None,
#     ) -> HTTPResponse:
#         """Execute HTTP request and return response"""
#         # Replace path parameters if provided
#         if path_params:
#             endpoint = self._replace_path_parameters(endpoint, path_params)


#         # Combine base URL and endpoint
#         url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

#         # Merge instance headers with method headers
#         request_headers = self.headers.copy()  # Start with instance headers
#         if headers:
#             request_headers.update(headers)  # Update with method-specific


#         try:
#             response = requests.request(
#                 method=method,
#                 url=url,
#                 params=query_params,
#                 headers=request_headers,
#                 json=body
#             )

#             return HTTPResponse(
#                 status_code=response.status_code,
#                 content=response.text,
#                 headers=dict(response.headers)
#             )

#         except requests.RequestException as e:
#             return HTTPResponse(
#                 status_code=500,
#                 content=str(e),
#                 headers={}
#             )

#     def _run(
#         self,
#         method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
#         base_url: str,
#         endpoint: str,
#         path_params: Optional[Dict[str, Any]] = None,
#         query_params: Optional[Dict[str, Any]] = None,
#         headers: Optional[Dict[str, str]] = None,
#         body: Optional[Dict[str, Any]] = None,
#     ) -> str:
#         """Run the HTTP request tool"""
#         try:
#             response = self._make_request(
#                 method=method,
#                 base_url=base_url,
#                 endpoint=endpoint,
#                 path_params=path_params,
#                 query_params=query_params,
#                 headers=headers,
#                 body=body
#             )

#             if response.status_code >= 400:
#                 return f"Error: HTTP {response.status_code} - {response.content}"

#             return response.content


#         except Exception as e:
#             return f"Error: {str(e)}"


# class EndpointEmbeddingManager:
#     def __init__(self, embedding_model: Embeddings = None):
#         self.embedding_model = embedding_model or OpenAIEmbeddings()
#         self.index = None
#         self.endpoints = []
#         self.endpoint_embeddings = None

#     def create_endpoint_text(self, endpoint: Tuple) -> str:
#         """Create a searchable text representation of the endpoint"""
#         try:
#             url, description = endpoint[0], endpoint[1]
            
#             #description = endpoint[2]['description']
#         except:
#             return "Error"
#         # return f"{method} {path} {description}"
#         return f"{url} {description}"
    
#     def embed_endpoints(self, endpoints: List[Tuple]) -> None:
#         """Create embeddings for all endpoints"""
#         self.endpoints = endpoints
#         texts = [self.create_endpoint_text(endpoint) for endpoint in endpoints]
#         embeddings = self.embedding_model.embed_documents(texts)

#         # Convert to numpy array and create FAISS index
#         self.endpoint_embeddings = np.array(embeddings, dtype=np.float32)
#         dimension = self.endpoint_embeddings.shape[1]

#         self.index = faiss.IndexFlatL2(dimension)
#         self.index.add(self.endpoint_embeddings)

#     def save_embeddings(self, file_path: str) -> None:
#         """Save embeddings and endpoints to disk"""
#         data = {
#             'endpoints': self.endpoints,
#             'embeddings': self.endpoint_embeddings
#         }
#         with open(file_path, 'wb') as f:
#             pickle.dump(data, f)

#     def load_embeddings(self, file_path: str) -> None:
#         """Load embeddings and endpoints from disk"""
#         with open(file_path, 'rb') as f:
#             data = pickle.load(f)

#         self.endpoints = data['endpoints']
#         self.endpoint_embeddings = data['embeddings']

#         dimension = self.endpoint_embeddings.shape[1]
#         self.index = faiss.IndexFlatL2(dimension)
#         # self.index = faiss.IndexFlatIP(dimension)
#         self.index.add(self.endpoint_embeddings)

#     def find_relevant_endpoints(self, query: str, k: int = 7) -> List[Tuple]:
#         """Find k most relevant endpoints for a given query.
#         Args:
#             query (str): Natural language description of the desired endpoint functionality
#                         e.g., "How to get company trades" or "create support pin"
#             k (int, optional): Number of relevant endpoints to return. Defaults to 5.
#         """        
#         query_embedding = self.embedding_model.embed_query(query)
#         query_embedding = np.array([query_embedding], dtype=np.float32)

#         distances, indices = self.index.search(query_embedding, k)
#         return [self.endpoints[i] for i in indices[0]]
from typing import Optional, Dict, Any, Literal, List
from pydantic import BaseModel, Field
import requests
import re

from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
import numpy as np
import json
import pickle
from typing import List, Tuple, Dict
import faiss
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langgraph.types import Command, interrupt


class HTTPResponse(BaseModel):
    """Model for HTTP responses"""
    status_code: int
    content: str
    headers: Dict[str, str]

class PathParameter(BaseModel):
    """Model for path parameters"""
    name: str
    description: str
    required: bool = True
    example: str = ""

class RequestBodySchema(BaseModel):
    """Model for request body schema"""
    type: str
    example: Dict[str, Any] = Field(default_factory=dict)

class APIEndpoint(BaseModel):
    """Model for API endpoint documentation"""
    method: str
    path: str
    description: str
    path_parameters: List[PathParameter] = Field(default_factory=list)
    request_body: Optional[RequestBodySchema] = None

class HTTPRequestTool(BaseModel):
    """Generic tool for making HTTP requests"""
    name: str = "http_request"
    description: str = """Make HTTP requests to API endpoints. Handles path parameters, query parameters, and request body.
    Required inputs:
    - method: HTTP method (GET, POST, PUT, DELETE, PATCH)
    - base_url: Base URL of the API
    - endpoint: API endpoint path (with path parameters in {param_name} format)
    Optional inputs:
    - path_params: Dictionary of path parameters to replace in the endpoint
    - query_params: Dictionary of query parameters
    - headers: Dictionary of request headers
    - body: Dictionary for request body (for POST/PUT/PATCH)
    """
    allow_dangerous_requests: bool = False
    headers: Dict[str, str] = Field(default_factory=dict) 

    class Config:
        arbitrary_types_allowed = True

    def _replace_path_parameters(self, endpoint: str, path_params: Dict[str, Any]) -> str:
        """Replace path parameters in endpoint URL"""
        for param_name, param_value in path_params.items():
            pattern = f"{{{param_name}}}"
            endpoint = endpoint.replace(pattern, str(param_value))
        return endpoint

    def _make_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        base_url: str,
        endpoint: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> HTTPResponse:
        """Execute HTTP request and return response"""
        # Replace path parameters if provided
        if path_params:
            endpoint = self._replace_path_parameters(endpoint, path_params)


        # Combine base URL and endpoint
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Merge instance headers with method headers
        request_headers = self.headers.copy()  # Start with instance headers
        if headers:
            request_headers.update(headers)  # Update with method-specific


        try:
            response = requests.request(
                method=method,
                url=url,
                params=query_params,
                headers=request_headers,
                json=body
            )

            return HTTPResponse(
                status_code=response.status_code,
                content=response.text,
                headers=dict(response.headers)
            )

        except requests.RequestException as e:
            return HTTPResponse(
                status_code=500,
                content=str(e),
                headers={}
            )

    def _run(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
        base_url: str,
        endpoint: str,
        path_params: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Run the HTTP request tool"""


        # human_review = interrupt(
        #     {
        #         "question": "Would you like to approve this API call?",
        #         # Surface tool calls for review
        #         "run_api_call":"",
        #     }
        # )
            
        try:



            # graph.invoke(Command(resume=value_from_human), config=thread_config)
            response = self._make_request(
                method=method,
                base_url=base_url,
                endpoint=endpoint,
                path_params=path_params,
                query_params=query_params,
                headers=headers,
                body=body
            )

            if response.status_code >= 400:
                return f"Error: HTTP {response.status_code} - {response.content}"



            status_messages = {
                200: "Success: The request was successfully processed.",
                201: "Created: A new resource was successfully created.",
                204: "No Content: The request was successful but there is no content to return.",
                400: "Bad Request: The server could not understand the request due to invalid syntax.",
                401: "Unauthorized: Authentication is required to access the requested resource.",
                403: "Forbidden: You do not have permission to access the requested resource.",
                404: "Not Found: The requested resource could not be found on the server.",
                500: "Internal Server Error: The server encountered an error and could not complete the request.",
                502: "Bad Gateway: The server received an invalid response from the upstream server.",
                503: "Service Unavailable: The server is currently unable to handle the request due to temporary overloading or maintenance.",
            }
            return status_messages.get(response.status_code, "Unknown status code."), response.content

        except Exception as e:
            return f"Error: {str(e)}"


class EndpointEmbeddingManager:
    def __init__(self, embedding_model: Embeddings = None):
        self.embedding_model = embedding_model or OpenAIEmbeddings()
        self.index = None
        self.endpoints = []
        self.endpoint_embeddings = None

    def create_endpoint_text(self, endpoint: Tuple) -> str:
        """Create a searchable text representation of the endpoint"""
        try:
            url, description = endpoint[0], endpoint[1]
            
            #description = endpoint[2]['description']
        except:
            return "Error"
        # return f"{method} {path} {description}"
        return f"{url} {description}"
    
    def embed_endpoints(self, endpoints: List[Tuple]) -> None:
        """Create embeddings for all endpoints"""
        self.endpoints = endpoints
        texts = [self.create_endpoint_text(endpoint) for endpoint in endpoints]
        embeddings = self.embedding_model.embed_documents(texts)

        # Convert to numpy array and create FAISS index
        self.endpoint_embeddings = np.array(embeddings, dtype=np.float32)
        dimension = self.endpoint_embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.endpoint_embeddings)

    def save_embeddings(self, file_path: str) -> None:
        """Save embeddings and endpoints to disk"""
        data = {
            'endpoints': self.endpoints,
            'embeddings': self.endpoint_embeddings
        }
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)

    def load_embeddings(self, file_path: str) -> None:
        """Load embeddings and endpoints from disk"""
        with open(file_path, 'rb') as f:
            data = pickle.load(f)

        self.endpoints = data['endpoints']
        self.endpoint_embeddings = data['embeddings']

        dimension = self.endpoint_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        # self.index = faiss.IndexFlatIP(dimension)
        self.index.add(self.endpoint_embeddings)

    def find_relevant_endpoints(self, query: str, k: int = 10) -> List[Tuple]:
        
        """Find k most relevant endpoints for a given query.
        Args:
            query (str): Natural language description of the desired endpoint functionality
                        e.g., "How to get company trades" or "create support pin"
            k (int, optional): Number of relevant endpoints to return. Defaults to 10, increase the k value in case the retrieved value are not fulfilling the query.
        """        
        query_embedding = self.embedding_model.embed_query(query)
        query_embedding = np.array([query_embedding], dtype=np.float32)

        distances, indices = self.index.search(query_embedding, k)
        return [self.endpoints[i] for i in indices[0]]
        # return [self.endpoints]