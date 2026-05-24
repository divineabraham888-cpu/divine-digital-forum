import os
from openai import OpenAI

# Initialize client using your API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def correct_text_grammar(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a professional assistant. Fix grammar and spelling errors. Keep the original meaning."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}") # Helpful for debugging
        return text  # Return original text if AI fails