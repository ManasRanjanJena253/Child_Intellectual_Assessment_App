import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.voice_utils import record_and_transcribe

def task():
    st.write("Make a sentence using the word ‘sun’")
    if st.button("🎙️ Start Recording"):
        with st.spinner("Listening..."):
            transcript = record_and_transcribe()
        st.write(f"Transcription: **{transcript}**")
        if "sun" in transcript and len(transcript.split()) >= 3:
            st.success("Nice sentence! ✅")
            return 3
        st.error("Try again!")
    return 0
