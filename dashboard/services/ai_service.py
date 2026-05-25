import os
from openai import OpenAI

# Safely check for the API key
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None
    print("WARNING: OPENAI_API_KEY is missing. AI grammar features will be temporarily disabled.")

# Keep the rest of your functions below, but add a safety check
def correct_text_grammar(text):
    if not client:
        return text # Just return the original text if AI is disabled
    
    # ... your existing OpenAI logic goes here ...