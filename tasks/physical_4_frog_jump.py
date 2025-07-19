import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import cv2, time
from utils.vision_utils import PoseDetector, vertical_jump
import mediapipe as mp

def task():
    st.write("🐸 Jump like a frog!")
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    start = time.time()
    frame_placeholder = st.empty()
    success = False
    prev_torso_y = None

    while cap.isOpened() and (time.time() - start < 15):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        landmarks = detector.get_landmarks(frame)

        if landmarks:
            if prev_torso_y is None:
                prev_torso_y = landmarks.landmark[mp.solutions.pose.PoseLandmark.NOSE.value].y
            if vertical_jump(landmarks, prev_torso_y):
                success = True
                break

        frame_placeholder.image(frame, channels="BGR")

    cap.release()
    frame_placeholder.empty()
    if success:
        st.success("Boing! Frog jump detected 🐸")
        st.balloons()
        return 3  # Return a score for successful completion
    else:
        st.error("⏰ Time's up! Try again.")
        return 0  # Return 0 for unsuccessful attempt

