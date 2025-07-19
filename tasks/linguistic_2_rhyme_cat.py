import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.voice_utils import record_and_transcribe

def task():
    st.write("Say a word that rhymes with ‘cat’")
    rhymes = {"bat", "hat", "mat", "rat", "sat", "fat"}
    if st.button("🎙️ Start Recording"):
        with st.spinner("Listening..."):
            transcript = record_and_transcribe()
        st.write(f"Transcription: **{transcript}**")
        if set(transcript.split()) & rhymes:
            st.success("Nice rhyme! ✅")
            return 3
        st.error("Try again!")
    return 0
