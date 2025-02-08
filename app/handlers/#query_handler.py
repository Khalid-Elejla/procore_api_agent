# app/handlers/query_handler.py
import base64
import logging
from ...backend.main import run_agent_graph


"""Query processing logic"""
class QueryHandler:
    def __init__(self, access_token):
        self.access_token = access_token

    def process_query(self, query, query_type="text"):
        try:
            if query_type == "audio":
                query = self._prepare_audio_query(query)
            return run_agent_graph(query=query)
        except Exception as e:
            logging.error(f"Query processing error: {str(e)}")
            raise

    def _prepare_audio_query(self, audio_data):
        return base64.b64encode(audio_data['bytes']).decode('utf-8')