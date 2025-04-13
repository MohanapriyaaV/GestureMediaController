# mediapipe_utils.py

import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize the hands model
hands_model = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def detect_hands_in_image(image):
    """Detect hands and return annotated image and landmark list."""
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands_model.process(image_rgb)

    landmarks_list = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
            landmarks_list.append(landmarks)

    return image, landmarks_list

def detect_hands_in_video(video_path, is_webcam=False):
    """Detect hands in video or webcam stream. Returns annotated frames."""
    cap = cv2.VideoCapture(0 if is_webcam else video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        annotated_frame, _ = detect_hands_in_image(frame)
        yield annotated_frame

    cap.release()
