import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.voice_utils import record_and_transcribe

def task():
    st.image("https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=200", width=200)
    st.write("What is this?")
    if st.button("🎙️ Start Recording"):
        with st.spinner("Listening..."):
            transcript = record_and_transcribe()
        st.write(f"Transcription: **{transcript}**")
        if "apple" in transcript:
            st.success("Great! ✅")
            return 3
        st.error("Try again!")
    return 0
