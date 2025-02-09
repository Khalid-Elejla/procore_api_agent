from langfuse.callback import CallbackHandler
import sys
import os
import contextlib
from io import StringIO

# from langchain_community.agent_toolkits.openapi.spec import reduce_openapi_spec, ReducedOpenAPISpec
from langchain_community.agent_toolkits.openapi.spec import ReducedOpenAPISpec
from langchain_core.utils.json_schema import dereference_refs

from packaging import version
import re
from typing import List, Tuple, Dict

# Define the langfuse handler (using environment variables for secret keys)
def get_langfuse_handler() -> CallbackHandler:
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_HOST")
    return CallbackHandler(secret_key=secret_key, public_key=public_key, host=host,)

# Define a context manager to suppress print statements
@contextlib.contextmanager
def suppress_print():
  # Save the current standard output
  original_stdout = sys.stdout
  # Redirect standard output to a null device
  sys.stdout = StringIO()
  try:
      yield
  finally:
      # Restore the original standard output
      sys.stdout = original_stdout


#================================================================================================

def reduce_openapi_spec(spec: dict, dereference: bool = True) -> ReducedOpenAPISpec:
    """Simplify/distill/minify a spec while preserving path-level parameters.

    Args:
        spec: The OpenAPI spec.
        dereference: Whether to dereference the spec. Default is True.

    Returns:
        ReducedOpenAPISpec: The reduced OpenAPI spec.
    """
    endpoints = []

    for route, path_item in spec["paths"].items():
        # Get path-level parameters (shared across operations)
        high_level_parameters = path_item.get("parameters", [])

        # Remove header parameters from high-level parameters
        high_level_parameters = [
            param for param in high_level_parameters 
            if param.get("in") != "header"
        ]

        

        # Process each operation
        for operation_name, docs in path_item.items():
            if operation_name not in ["get", "post", "patch", "put", "delete"]:
                continue

            # Create a copy of the operation docs to avoid modifying the original
            operation_docs = docs.copy()

            # Combine path-level parameters with operation-level parameters
            operation_parameters = operation_docs.get("parameters", [])
            combined_parameters = high_level_parameters + operation_parameters

            # Update the operation docs with combined parameters
            if combined_parameters:
                operation_docs["parameters"] = combined_parameters

            endpoints.append(
                (f"{operation_name.upper()} {route}",
                #  operation_docs.get("summary"),
                 operation_docs.get("description"),
                #  operation_docs.get("tags"),
                 operation_docs)
            )

    # 2. Replace any refs if requested
    if dereference:
        endpoints = [
            (name, description, dereference_refs(docs, full_schema=spec))
            for name, description, docs in endpoints
        ]

    # 3. Strip docs down to required request args + happy path response
    def reduce_endpoint_docs(docs: dict) -> dict:
        out = {}
        if docs.get("description"):
            out["description"] = docs.get("description")
        if docs.get("parameters"):
            # Keep required parameters and all path/header parameters
            out["parameters"] = [
                parameter
                for parameter in docs.get("parameters", [])
                if parameter.get("required") or parameter.get("in") in ["path"]#, "header"]
            ]
        # if "200" in docs.get("responses", {}):
        #     out["responses"] = docs["responses"]["200"]
        if docs.get("requestBody"):
            out["requestBody"] = docs.get("requestBody")
        return out

    endpoints = [
        (name, description, reduce_endpoint_docs(docs))
        for name, description, docs in endpoints
    ]

    return ReducedOpenAPISpec(
        servers=spec["servers"],
        description=spec["info"].get("description", ""),
        endpoints=endpoints,
    )




def get_version_from_path(path: str) -> version.Version:
    """Extract version number from API path and convert to Version object for comparison.

    Args:
        path: API endpoint path

    Returns:
        Version object or Version("0.0") if no version found
    """
    version_pattern = r'v(\d+(?:\.\d+)*)'
    match = re.search(version_pattern, path)
    if match:
        return version.parse(match.group(1))
    return version.parse("0.0")

def group_endpoints_by_base_path(endpoints: List[Tuple]) -> Dict[str, List[Tuple]]:
    """Group endpoints by their base path (excluding version).

    Args:
        endpoints: List of endpoint tuples (name, description, docs)

    Returns:
        Dictionary with base paths as keys and list of endpoints as values
    """
    grouped = {}
    for endpoint in endpoints:
        name = endpoint[0]
        # Extract base path by removing version part
        base_path = re.sub(r'/v\d+(?:\.\d+)*/', '/{version}/', name)
        if base_path not in grouped:
            grouped[base_path] = []
        grouped[base_path].append(endpoint)
    return grouped


def enhanced_reduce_openapi_spec(spec: dict, dereference: bool = True, latest_version_only: bool = False) -> ReducedOpenAPISpec:
    """Enhanced version of reduce_openapi_spec with option to keep only latest API versions.

    Args:
        spec: The OpenAPI spec
        dereference: Whether to dereference the spec
        latest_version_only: If True, only keeps the latest version of each endpoint

    Returns:
        ReducedOpenAPISpec: The reduced OpenAPI spec
    """
    # First get the reduced spec using original function
    reduced_spec = reduce_openapi_spec(spec, dereference)

    if not latest_version_only:
        return reduced_spec

    # Process endpoints to keep only latest versions
    endpoints = reduced_spec.endpoints

    # Group endpoints by their base path
    grouped_endpoints = group_endpoints_by_base_path(endpoints)

    # For each group, keep only the endpoint with the latest version
    latest_endpoints = []
    for base_path, endpoint_group in grouped_endpoints.items():
        if len(endpoint_group) == 1:
            latest_endpoints.extend(endpoint_group)
        else:
            # Sort endpoints by version and keep the latest
            latest = max(endpoint_group,
                        key=lambda x: get_version_from_path(x[0]))
            latest_endpoints.append(latest)

    # Create new ReducedOpenAPISpec with filtered endpoints
    return ReducedOpenAPISpec(
        servers=reduced_spec.servers,
        description=reduced_spec.description,
        endpoints=latest_endpoints
    )