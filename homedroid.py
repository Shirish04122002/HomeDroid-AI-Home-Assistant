import os
import sys
import queue
import sounddevice as sd
import vosk
import subprocess
import json
import streamlit as st
from streamlit_chat import message
from gtts import gTTS
from io import BytesIO

# Vosk model setup
samplerate = 16000
model_path = "vosk-model"

if not os.path.exists(model_path):
    st.error("Please download the Vosk model and unpack it as 'vosk-model' in the current folder.")
    sys.exit(1)

model = vosk.Model(model_path)
rec = vosk.KaldiRecognizer(model, samplerate)
q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}", file=sys.stderr)
    q.put(bytes(indata))

def process_llama_output(output):
    response = output.split('Assistant:')[-1].strip()
    return response

def recognize_speech_vosk():
    """Capture speech and convert to text using Vosk."""
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=1, callback=callback):
        data = q.get()
        if rec.AcceptWaveform(data):
            result = rec.Result()
            return json.loads(result).get("text", "")
    return ""

def generate_llama_response(prompt):
    """Generate a response using LLaMA CLI."""
    formatted_prompt = f"[INST] {prompt} [/INST]"
    llama_cmd = [
        './llama.cpp/llama-cli',
        '-m', '~/models/adapter_model.gguf',
        '--prompt', formatted_prompt,
        '--n-predict', '50'
    ]
    try:
        llama_output = subprocess.check_output(llama_cmd, text=True)
        return process_llama_output(llama_output)
    except subprocess.CalledProcessError as e:
        return f"Error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

def text_to_speech(text):
    tts = gTTS(text)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

st.set_page_config(page_title="HomeDroid-AI Assistant", layout="wide")

st.title("\U0001F916 HomeDroid-AI Home Assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def handle_user_input(user_text):
    if user_text:
        st.session_state["messages"].append({"role": "user", "content": user_text})
        ai_response = generate_llama_response(user_text)
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})
        return ai_response

# Chat interface
st.subheader("Chat with HomeDroid-AI")
chat_container = st.container()

with chat_container:
    for message_data in st.session_state["messages"]:
        message(message_data["content"], is_user=(message_data["role"] == "user"))

    user_input_col, voice_input_col = st.columns([2, 1])

    with user_input_col:
        user_text = st.text_input("Type your message:")
        if user_text:
            ai_response = handle_user_input(user_text)
            st.audio(text_to_speech(ai_response), format="audio/mp3")

    with voice_input_col:
        if st.button("🎙️ Speak"):
            voice_text = recognize_speech_vosk()
            if voice_text:
                st.session_state["user_input"] = voice_text
                ai_response = handle_user_input(voice_text)
                st.audio(text_to_speech(ai_response), format="audio/mp3")

# Clear conversation button
if st.sidebar.button("Clear Conversation"):
    st.session_state["messages"] = []
