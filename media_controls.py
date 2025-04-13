import cv2
import mediapipe as mp

# MediaPipe Setup for Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

def detect_hands_in_video(video_path=None, is_webcam=True):
    """
    Detect hands in video from webcam or video file and yield processed frames.
    Args:
        video_path (str): Path to video file (None if using webcam).
        is_webcam (bool): Flag to indicate whether to use webcam or video.
    Yields:
        tuple: (frame, landmarks) where frame is the processed image, and landmarks is the list of landmarks.
    """
    cap = cv2.VideoCapture(0 if is_webcam else video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)
        landmarks = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Collect landmarks for each hand
                hand_coords = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                landmarks.append(hand_coords)
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        yield frame, landmarks

    cap.release()

def get_finger_states(landmarks):
    """
    Determine if each finger is up (extended) or down (folded).
    Returns a list like [thumb, index, middle, ring, pinky] where 1=up, 0=down.
    Args:
        landmarks: List of (x, y, z) coordinates for the 21 hand landmarks.
    Returns:
        List of 5 binary values (0 or 1) for each finger state.
    """
    fingers = []
    
    # Thumb detection (different for left vs right hand)
    is_right_hand = landmarks[4][0] > landmarks[0][0]  # Determine if it's the right hand
    
    if is_right_hand:
        # Right hand - thumb is up if thumb tip is to the right of thumb IP joint
        fingers.append(1 if landmarks[4][0] > landmarks[3][0] else 0)
    else:
        # Left hand - thumb is up if thumb tip is to the left of thumb IP joint
        fingers.append(1 if landmarks[4][0] < landmarks[3][0] else 0)
    
    # For other fingers, check if the tip is above the PIP joint (indicates it's up)
    for finger_id in range(1, 5):
        tip_id = finger_id * 4 + 4  # Index of the fingertip landmark
        pip_id = finger_id * 4 + 2  # Index of the PIP joint landmark
        
        if landmarks[tip_id][1] < landmarks[pip_id][1]:
            fingers.append(1)  # Finger is up
        else:
            fingers.append(0)  # Finger is down
    
    return fingers

def map_gesture_to_action(landmarks):
    """
    Map hand gesture based on landmarks to media control action.
    Args:
        landmarks: List of landmark lists for detected hands.
    Returns:
        String with the action name: 'play', 'pause', 'stop', 'next', 'previous', or None.
    """
    if not landmarks or len(landmarks) == 0:
        return None
    
    # Get finger states for the first detected hand
    finger_states = get_finger_states(landmarks[0])
    
    # Open palm (all fingers up) = play
    if sum(finger_states) == 5:
        return "play"
    
    # Closed fist (all fingers down) = pause
    elif sum(finger_states) == 0:
        return "pause"
    
    # Check for palm down gesture (stop)
    palm_facing_down = landmarks[0][0][1] < landmarks[0][9][1]
    if palm_facing_down and sum(finger_states[1:]) >= 3:  # at least 3 fingers extended
        return "stop"
    
    # Peace sign - index and middle fingers up, others down
    elif finger_states == [0, 1, 1, 0, 0]:
        return "next"
    
    # Index finger up only - one finger pointing
    elif finger_states == [0, 1, 0, 0, 0]:
        return "previous"
    
    # If no recognizable gesture, return None
    return None
