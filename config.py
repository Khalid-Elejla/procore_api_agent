# app/config.py

import base64
from backend.main import run_agent_graph
from streamlit_mic_recorder import mic_recorder

"""Application configuration and constants"""
APP_TITLE = "Procore AI Assistant"
ALLOWED_FILE_TYPES = ["pdf", "docx", "txt", "xls"]

# app/state.py
"""Session state management"""
def initialize_session_state(st):
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

# app/ui/components.py
"""UI components and layouts"""
def render_sidebar(st):
    with st.sidebar:
        st.subheader("📂 File Upload")
        uploaded_file = st.file_uploader("Upload your document",
                                       type=ALLOWED_FILE_TYPES)
        return uploaded_file

def render_chat_interface(st):
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        text_input = st.chat_input("Type your question here...")
    with col2:
        audio_input = mic_recorder(
            start_prompt="🎤 Speak",
            stop_prompt="⏹️ Stop",
            format="wav",
            key='recorder'
        )
    return text_input, audio_input

# app/handlers/query_handler.py
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