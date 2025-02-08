# app/ui/components.py
from config import ALLOWED_FILE_TYPES
from streamlit_mic_recorder import mic_recorder

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
