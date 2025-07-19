import mediapipe as mp
import cv2

mp_pose = mp.solutions.pose
POSE_LMS = mp_pose.PoseLandmark

class PoseDetector:
    """Wrapper around MediaPipe Pose to extract landmarks."""
    def __init__(self, static_image_mode=False):
        self.pose = mp_pose.Pose(static_image_mode=static_image_mode)

    def get_landmarks(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)
        return results.pose_landmarks

def wrists_above_head(landmarks):
    if not landmarks: return False
    nose_y = landmarks.landmark[POSE_LMS.NOSE].y
    lw_y = landmarks.landmark[POSE_LMS.LEFT_WRIST].y
    rw_y = landmarks.landmark[POSE_LMS.RIGHT_WRIST].y
    return lw_y < nose_y and rw_y < nose_y

def one_leg_up(landmarks):
    if not landmarks: return False
    l_knee_y = landmarks.landmark[POSE_LMS.LEFT_KNEE].y
    r_knee_y = landmarks.landmark[POSE_LMS.RIGHT_KNEE].y
    l_hip_y  = landmarks.landmark[POSE_LMS.LEFT_HIP].y
    r_hip_y  = landmarks.landmark[POSE_LMS.RIGHT_HIP].y
    return (l_knee_y < l_hip_y and r_knee_y > r_hip_y) or (r_knee_y < r_hip_y and l_knee_y > l_hip_y)

def torso_rotation(landmarks, initial_angle, threshold=140):
    if not landmarks: return False
    l_sh = landmarks.landmark[POSE_LMS.LEFT_SHOULDER]
    r_sh = landmarks.landmark[POSE_LMS.RIGHT_SHOULDER]
    current_angle = r_sh.x - l_sh.x
    return abs(current_angle - initial_angle) > threshold / 180.0

def minimal_movement(prev_landmarks, curr_landmarks, thresh=0.02):
    if not prev_landmarks or not curr_landmarks: return False
    deltas = [abs(pl.x - cl.x) + abs(pl.y - cl.y) for pl, cl in zip(prev_landmarks.landmark, curr_landmarks.landmark)]
    return max(deltas) < thresh

def vertical_jump(landmarks, prev_torso_y, jump_thresh=0.05):
    if not landmarks or prev_torso_y is None: return False
    torso_y = landmarks.landmark[POSE_LMS.NOSE].y
    return prev_torso_y - torso_y > jump_thresh

def forward_jump(landmarks, initial_nose_x, jump_thresh=0.07):
    if not landmarks: return False
    nose_x = landmarks.landmark[POSE_LMS.NOSE].x
    return abs(nose_x - initial_nose_x) > jump_thresh
