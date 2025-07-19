import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import cv2, time
from utils.vision_utils import PoseDetector, forward_jump
import mediapipe as mp

def task():
    st.write("🦘 Do a big kangaroo jump forward!")
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    start = time.time()
    frame_placeholder = st.empty()
    success = False
    initial_nose_x = None

    while cap.isOpened() and (time.time() - start < 15):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        landmarks = detector.get_landmarks(frame)

        if landmarks:
            if initial_nose_x is None:
                initial_nose_x = landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE.value].x
            if forward_jump(landmarks, initial_nose_x):
                success = True
                break

        frame_placeholder.image(frame, channels="BGR")

    cap.release()
    frame_placeholder.empty()
    if success:
        st.success("Hop hop! Kangaroo jump detected 🦘")
        st.balloons()
        return 3  # Return a score for successful completion
    else:
        st.error("⏰ Time's up! Try again.")
        return 0  # Return 0 for unsuccessful attempt
