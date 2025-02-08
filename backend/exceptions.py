# backend/exceptions.py
class GraphBuildError(Exception):
    """Raised when graph building fails"""
    pass

class QueryProcessingError(Exception):
    """Raised when query processing fails"""
    pass

class EnvironmentError(Exception):
    """Raised when required environment variables are missing"""
    pass