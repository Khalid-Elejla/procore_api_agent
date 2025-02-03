# # openai_models.py

import os
from langchain_openai import ChatOpenAI

# Load API keys (environment variables can be set before running the app)
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

# Function to initialize the OpenAI LLM with API key
def load_openai_model(temperature=0, model="gpt-4o-mini"):
    if OPENAI_API_KEY:
        return ChatOpenAI(temperature=temperature, model=model)
    else:
        raise ValueError("OpenAI API key not set. Please set OPENAI_API_KEY as an environment variable.")

# import os
# from langchain_anthropic import ChatAnthropic

# # Load API keys (environment variables can be set before running the app)
# ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# # Function to initialize the Anthropic LLM with API key
# def load_openai_model(temperature=0, model="claude-3-haiku-20240307"):
#     if ANTHROPIC_API_KEY:
#         return ChatAnthropic(temperature=temperature, model=model)
#     else:
#         raise ValueError("Anthropic API key not set. Please set ANTHROPIC_API_KEY as an environment variable.")
