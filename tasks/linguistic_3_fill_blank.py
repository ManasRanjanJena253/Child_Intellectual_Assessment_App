import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from utils.voice_utils import record_and_transcribe

def task():
    st.image("https://images.unsplash.com/photo-1525253086316-d0c936c814f8?w=300", width=300)
    st.write("The dog is sleeping on the ___")
    if st.button("🎙️ Start Recording"):
        with st.spinner("Listening..."):
            transcript = record_and_transcribe()
        st.write(f"Transcription: **{transcript}**")
        expected = {"mat", "bed", "sofa", "couch", "floor"}
        if set(transcript.split()) & expected:
            st.success("Correct! ✅")
            return 3
        st.error("Try again!")
    return 0
