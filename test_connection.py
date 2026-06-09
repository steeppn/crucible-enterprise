# test_connection.py
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from the hidden .env file
load_dotenv()
print(f"DEBUG: .env file found and loaded: {"loaded"}")
print(f"DEBUG: API Key found: {bool(os.getenv('OPENCODE_ZEN_API_KEY'))}")

base_url = os.getenv("OPENCODE_BASE_URL")
api_key = os.getenv("OPENCODE_ZEN_API_KEY")
target_model = os.getenv("TARGET_MODEL")

# Initialize the client pointing to OpencCode endpoint
client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

try:
    print("Contacting model via OpenCode API...")
    response = client.chat.completions.create(
        model=target_model,
        messages=[
            {"role": "system", "content": "You are a helpful hackathon assistant."},
            {"role": "user", "content": "Say 'CRUCIBLE Enterprise is online' if you can hear me."}
        ]
    )
    print("Success! Response from LLM:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nConnection Failed. Check your API key or endpoint config.")
    print(f"Error details: {e}")