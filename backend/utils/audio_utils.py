import io
import os
import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from IPython.display import Image, display

import logging

from openai import OpenAI

from elevenlabs import play, VoiceSettings
from elevenlabs.client import ElevenLabs

from langgraph.graph import StateGraph, MessagesState, END, START
from langchain_core.messages import HumanMessage, SystemMessage
from ..states.state import UnifiedState

import streamlit as st
from langchain_core.runnables import RunnableConfig
import base64

# Initialize OpenAI client
openai_client = OpenAI()

# Initialize ElevenLabs client
elevenlabs_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def record_audio_until_stop(state: UnifiedState):

    # Retrieve audio bytes from metadata
    # audio_bytes = config.get("metadata", {}).get("audio_bytes")

    # logging.info("Here is the transcription:", type(state))
    logging.info("Here is the transcription: %s", type(state))

    audio_bytes=state['voice_query']


    # Convert Base64 string back to bytes
    audio_bytes = base64.b64decode(audio_bytes)

    # """Records audio from the microphone until Enter is pressed, then saves it to a .wav file."""
    
    # audio_data = []  # List to store audio chunks
    # recording = True  # Flag to control recording
    # sample_rate = 16000 # (kHz) Adequate for human voice frequency

    # def record_audio():
    #     """Continuously records audio until the recording flag is set to False."""
    #     nonlocal audio_data, recording
    #     with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
    #         print("Recording your instruction! ... Press Enter to stop recording.")
    #         while recording:
    #             audio_chunk, _ = stream.read(1024)  # Read audio data in chunks
    #             audio_data.append(audio_chunk)

    # def stop_recording():
    #     """Waits for user input to stop the recording."""
    #     input()  # Wait for Enter key press
    #     nonlocal recording
    #     recording = False
    # # logging.info("starting recording thread")
    # # Start recording in a separate thread
    # recording_thread = threading.Thread(target=record_audio)
    # recording_thread.start()
    
    # # logging.info("start to stop_thread")
    # # Start a thread to listen for the Enter key
    # stop_thread = threading.Thread(target=stop_recording)
    # stop_thread.start()

    # # Wait for both threads to complete
    # stop_thread.join()
    # recording_thread.join()

    # # Stack all audio chunks into a single NumPy array and write to file
    # audio_data = np.concatenate(audio_data, axis=0)
    
    # # Convert to WAV format in-memory
    # audio_bytes = io.BytesIO()

    #write(audio_bytes, sample_rate, audio_data)  # Use scipy's write function to save to BytesIO
    # audio_bytes.seek(0)  # Go to the start of the BytesIO buffer
    # audio_bytes.name = "audio.wav" # Set a filename for the in-memory file

    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.mp3"
    logging.info("Here is the transcription:", type(audio_bytes))

    # Transcribe via Whisper
    transcription = openai_client.audio.transcriptions.create(
       model="whisper-1", 
    #    file=audio_bytes,
       file=audio_file,
       language="en" 
    )

    # Print the transcription
    logging.info("Here is the transcription:", transcription.text)

    # Write to messages 
    st.write(f"User: {transcription.text}")
    return {"query": [HumanMessage(content=transcription.text)]}


def play_audio(state: UnifiedState):
    
    """Plays the audio response from the remote graph with ElevenLabs."""

    # Response from the agent 
    try:
        # logging.info(state)
        response = state['api_agent_messages'][-1]
    except:
        # logging.info(state)
        response = state['api_agent_messages'][-1]
    # Prepare text by replacing ** with empty strings
    # These can cause unexpected behavior in ElevenLabs
    cleaned_text = response.content.replace("**", "")
    st.write(f"assistant: {cleaned_text}")
    

    import openai
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Other voices: "echo", "fable", "onyx", "nova", "shimmer"
        input=cleaned_text
    )
    response=response.read()
    # Call text_to_speech API with turbo model for low latency
    # response = elevenlabs_client.text_to_speech.convert(
    #     voice_id="pNInz6obpgDQGcFmaJgB", # Adam pre-made voice
    #     output_format="mp3_22050_32",
    #     text=cleaned_text,
    #     model_id="eleven_turbo_v2_5", 
    #     voice_settings=VoiceSettings(
    #         stability=0.0,
    #         similarity_boost=1.0,
    #         style=0.0,
    #         use_speaker_boost=True,
    #     ),
    # )
    
    # Play the audio back
    play(response)
    return {'messages':[cleaned_text]}

