import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import openai
import requests

app = Flask(__name__)

# Load the .env credentials
# openai.api_key = 'YOUR_OPEN_AI_KEY'  # Replace with your actual key

ELEVENLABS_URL = "https://api.elevenlabs.com/text-to-speech"
# ELEVENLABS_KEY = 'YOUR_ELEVENLABS_KEY'  # Replace with your actual key

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")
ELEVENLABS_KEY = os.getenv("ELEVENLABS_KEY")

@app.route('/chat', methods=['POST'])
def chat():
    user_text = request.json['text']
    # Use OpenAI to get a response
    response = openai.Completion.create(engine="davinci", prompt=user_text, max_tokens=150)
    assistant_text = response.choices[0].text.strip()

    # Convert assistant's response to audio
    audio_response = requests.post(
        ELEVENLABS_URL,
        headers={'Authorization': ELEVENLABS_KEY},
        json={"text": assistant_text}
    )
    audio_content = audio_response.content if audio_response.status_code == 200 else None

    return jsonify({"audio": audio_content, "text": assistant_text})

if __name__ == '__main__':
    app.run(debug=True)
