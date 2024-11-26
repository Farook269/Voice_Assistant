import streamlit as st
import os
import time
from deepgram import DeepgramClient, SpeakOptions
from groq import Groq
from stt import transcribe_audio
from speech_recg import record_audio
import pygame
import numpy as np
import tempfile


# Set environment variables
os.environ['DG_API_KEY'] = "fc56f9e7cc7adc88c6cbdbec83883043da3b66e3"
os.environ['GROQ_API_KEY'] = "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"

# Set page config for dark theme
st.set_page_config(page_title="Voice Assistant", page_icon="🔊", layout="wide", initial_sidebar_state="collapsed")

# Apply custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #333333;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def text_to_speech(text):
    SPEAK_OPTIONS = {"text": text}
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        filename = temp_file.name
    try:
        deepgram = DeepgramClient(api_key=os.getenv("DG_API_KEY"))
        options = SpeakOptions(
            model="aura-stella-en",
            encoding="linear16",
            container="wav"
        )
        response = deepgram.speak.v("1").save(filename, SPEAK_OPTIONS, options)
        st.success("Text-to-speech conversion completed.")
        return filename
    except Exception as e:
        st.error(f"Text-to-speech Exception: {e}")
        return None

def groq_chat(transcript):
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": transcript,
            },
          
        ],
        model="gemma2-9b-it",
    )
    return chat_completion.choices[0].message.content

def play_audio(file_path):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.quit()

def detect_silence(audio_data, sample_rate, threshold=100, duration=0.5):
    chunk_size = int(sample_rate * duration)
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i+chunk_size]
        if np.max(np.abs(chunk)) > threshold:
            return False
    return True

def main():
    st.title("🔊 Voice Assistant")
    st.write("Welcome to your AI-powered voice assistant!")

    if 'conversation' not in st.session_state:
        st.session_state.conversation = []

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start Conversation"):
            with st.spinner("Listening..."):
                silence_duration = 0
                while silence_duration < 5:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                        audio_file_path = temp_file.name
                    audio_data, sample_rate = record_audio(audio_file_path, duration=5, return_data=True)
                    
                    if detect_silence(audio_data, sample_rate):
                        silence_duration += 5
                        st.info(f"Silence detected. Total silence: {silence_duration} seconds")
                    else:
                        silence_duration = 0
                        st.info("Transcribing audio...")
                        transcript = transcribe_audio(audio_file_path)
                        
                        if transcript:
                            st.session_state.conversation.append(("You", transcript))
                            st.info("Processing your input...")
                            try:
                                groq_output = groq_chat(transcript)
                                st.session_state.conversation.append(("Assistant", groq_output))
                                
                                output_file = text_to_speech(groq_output)
                                
                                if output_file:
                                    st.success("Playing response...")
                                    play_audio(output_file)
                                else:
                                    st.error("Failed to generate audio output.")
                            except Exception as e:
                                st.error(f"Error during processing: {e}")
                        else:
                            st.warning("Couldn't understand the audio. Please try again.")
                
                st.success("Conversation ended due to 5 seconds of silence.")

    with col2:
        st.subheader("Conversation History")
    for i, (speaker, message) in enumerate(st.session_state.conversation):
        if speaker == "You":
            st.text_input("You:", value=message, key=f"user_input_{i}", disabled=True)
        else:
            st.text_area("Assistant:", value=message, key=f"assistant_output_{i}", disabled=True)

if __name__ == "__main__":
    main()