import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.voice_utils import record_and_transcribe
import re

def task():
    st.write("Say ‘ma‑ma’")
    if st.button("🎙️ Start Recording"):
        with st.spinner("Listening..."):
            transcript = record_and_transcribe()
        st.write(f"Transcription: **{transcript}**")
        if re.search(r'\b(ma|mama|mumma|mummy)\b', transcript):
            st.success("Great! ✅")
            return 3
        st.error("Let's try again!")
    return 0
