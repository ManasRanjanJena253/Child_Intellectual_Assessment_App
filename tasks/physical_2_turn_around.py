import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import cv2, time
from utils.vision_utils import PoseDetector, torso_rotation
import mediapipe as mp

def task():
    st.write("🌀 Turn around once!")
    detector = PoseDetector()
    cap = cv2.VideoCapture(0)
    start = time.time()
    frame_placeholder = st.empty()
    success = False
    initial_angle = None

    while cap.isOpened() and (time.time() - start < 15):
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        landmarks = detector.get_landmarks(frame)

        if landmarks:
            l_sh = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
            r_sh = landmarks.landmark[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
            if initial_angle is None:
                initial_angle = r_sh.x - l_sh.x
            if torso_rotation(landmarks, initial_angle):
                success = True
                break

        frame_placeholder.image(frame, channels="BGR")

    cap.release()
    frame_placeholder.empty()
    if success:
        st.success("Nice spin! Full turn detected 🌀")
        st.balloons()
        return 3  # Return a score for successful completion
    else:
        st.error("⏰ Time's up! Try again.")
        return 0  # Return 0 for unsuccessful attempt

