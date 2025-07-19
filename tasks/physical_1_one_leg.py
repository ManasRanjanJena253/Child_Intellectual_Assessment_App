import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import cv2, time
from utils.vision_utils import PoseDetector, one_leg_up

def task():
    st.write("🦩 Lift one leg like a bird!")
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    start = time.time()
    frame_placeholder = st.empty()
    success = False

    while cap.isOpened() and (time.time() - start < 15):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        landmarks = detector.get_landmarks(frame)

        if landmarks and one_leg_up(landmarks):
            success = True
            break

        frame_placeholder.image(frame, channels="BGR")

    cap.release()
    frame_placeholder.empty()
    if success:
        st.success("Awesome balance! One leg up 🦩")
        st.balloons()
        return 3  # Return a score for successful completion
    else:
        st.error("⏰ Time's up! Try again.")
        return 0  # Return 0 for unsuccessful attempt

