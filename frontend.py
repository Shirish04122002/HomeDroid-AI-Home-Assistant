import streamlit as st
from streamlit_chat import message
from gtts import gTTS
from io import BytesIO
import speech_recognition as sr
import requests

def text_to_speech(text):
    tts = gTTS(text)
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening...")
        try:
            audio_data = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return ""
        except sr.WaitTimeoutError:
            return ""

def query_homedroid_ai(prompt):
    """Sends a query to the HomeDroid-AI backend and retrieves a response."""
    # Replace URL with your actual backend API endpoint
    backend_url = "http://your-backend-api-url.com/query"
    try:
        response = requests.post(backend_url, json={"prompt": prompt})
        response.raise_for_status()
        return response.json().get("response", "Sorry, I didn't get that.")
    except requests.RequestException as e:
        return f"Error: Unable to reach the HomeDroid-AI backend. ({e})"

st.set_page_config(page_title="HomeDroid-AI Assistant", layout="wide")

st.title("\U0001F916 HomeDroid-AI Home Assistant")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "user_input" not in st.session_state:
    st.session_state["user_input"] = ""

def handle_user_input():
    user_text = st.session_state["user_input"].strip()
    if user_text:
        st.session_state["messages"].append({"role": "user", "content": user_text})
        ai_response = query_homedroid_ai(user_text)
        st.session_state["messages"].append({"role": "assistant", "content": ai_response})
        st.session_state["user_input"] = ""
        return ai_response

# Chat interface
st.subheader("Chat with HomeDroid-AI")
chat_container = st.container()

with chat_container:
    for message_data in st.session_state["messages"]:
        message(message_data["content"], is_user=(message_data["role"] == "user"))

    user_input_col, voice_input_col = st.columns([2, 1])

    with user_input_col:
        st.text_input(
            "Type your message:",
            key="user_input",
            on_change=handle_user_input
        )

    with voice_input_col:
        if st.button("🎙️ Speak"):
            voice_text = recognize_speech()
            if voice_text:
                st.session_state["user_input"] = voice_text
                ai_response = handle_user_input()
                st.audio(text_to_speech(ai_response), format="audio/mp3")

# Clear conversation button
if st.sidebar.button("Clear Conversation"):
    st.session_state["messages"] = []
