import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.voice_utils import record_and_transcribe
import re

def task():
    st.image("https://images.unsplash.com/photo-1503264116251-35a269479413?w=400", width=400)
    st.write("Tell a short story about this picture.")
    if st.button("🎙️ Start Recording"):
        with st.spinner("Listening..."):
            transcript = record_and_transcribe()
        st.write(f"Transcription: **{transcript}**")
        if "kite" in transcript and len(re.findall(r'[.!?]', transcript)) >= 2:
            st.success("Great story! ✅")
            return 3
        st.error("Try again!")
    return 0
