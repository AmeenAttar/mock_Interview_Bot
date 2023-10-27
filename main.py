from fastapi import FastAPI, WebSocket, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
import openai
import os
import json
import requests
from dotenv import load_dotenv
import tempfile

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")
elevenlabs_key = os.getenv("ELEVENLABS_KEY")

app = FastAPI()

origins = [
    "http://localhost:5174",
    "http://localhost:5173",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        audio_data = await websocket.receive_bytes()
        with tempfile.NamedTemporaryFile(delete=True, suffix=".wav") as temp_audio_file:
            temp_audio_file.write(audio_data)
            temp_audio_file.flush()  
            
            try:
                with open(temp_audio_file.name, 'rb') as audio:
                    transcript = openai.Audio.transcribe("whisper-1", audio)
                response_text = get_chat_response(transcript)
                response_audio = text_to_speech(response_text)
                await websocket.send_bytes(response_audio)
            except openai.error.InvalidRequestError as e:
                await websocket.send_text(f"Error: {str(e)}")

def get_chat_response(user_message):
    messages = load_messages()
    messages.append({"role": "user", "content": user_message['text']})
    gpt_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    parsed_gpt_response = gpt_response['choices'][0]['message']['content']
    save_messages(user_message['text'], parsed_gpt_response)
    return parsed_gpt_response

def load_messages():
    messages = []
    file = 'database.json'
    if os.stat(file).st_size != 0:
        with open(file) as db_file:
            data = json.load(db_file)
            messages.extend(data)
    else:
        messages.extend([
            {"role": "system", "content": "You are a consular officer conducting an F1 visa interview."},
            {"role": "user", "content": "Good morning."},
            {"role": "assistant", "content": "Good morning. Can I have your passport and I-20 form, please?"}
        ])
    return messages

def save_messages(user_message, gpt_response):
    file = 'database.json'
    messages = load_messages()
    messages.append({"role": "user", "content": user_message})
    messages.append({"role": "assistant", "content": gpt_response})
    with open(file, 'w') as f:
        json.dump(messages, f)

def text_to_speech(text):
    voice_id = 'pNInz6obpgDQGcFmaJgB'
    body = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0,
            "style": 0.5,
            "use_speaker_boost": True
        }
    }

    headers = {
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
        "xi-api-key": elevenlabs_key
    }

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    try:
        response = requests.post(url, json=body, headers=headers)
        if response.status_code == 200:
            return response.content
        else:
            print('Error: Text-to-Speech API call failed.')
    except Exception as e:
        print(f"Exception: {e}")
