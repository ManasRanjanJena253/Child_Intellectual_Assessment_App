import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import cv2, time
from utils.vision_utils import PoseDetector, minimal_movement

def task():
    st.write("🕴 Stand still like a statue for 2 s!")
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    start = time.time()
    frame_placeholder = st.empty()
    prev_landmarks = None
    success = False

    while cap.isOpened() and (time.time() - start < 15):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        curr_landmarks = detector.get_landmarks(frame)

        if curr_landmarks and prev_landmarks and minimal_movement(prev_landmarks, curr_landmarks):
            success = True
            break

        prev_landmarks = curr_landmarks
        frame_placeholder.image(frame, channels="BGR")

    cap.release()
    frame_placeholder.empty()
    if success:
        st.success("Statue mode complete! 🗿")
        st.balloons()
        return 3  # Return a score for successful completion
    else:
        st.error("⏰ Time's up! Try again.")
        return 0  # Return 0 for unsuccessful attempt
