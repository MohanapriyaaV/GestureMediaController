# mediapipe_utils.py
import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Initialize the hands model with better parameters
hands_model = mp_hands.Hands(
    static_image_mode=True,  # Set to False for video streams
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# For video streams, we'll use a separate model instance
video_hands_model = mp_hands.Hands(
    static_image_mode=False,  # Better for tracking in videos
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def detect_hands_in_image(image):
    """Detect hands and return annotated image and landmark list."""
    # Check if image is empty or invalid
    if image is None or image.size == 0:
        return image, []
    
    # Convert the image to RGB format for MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image with MediaPipe Hands
    results = hands_model.process(image_rgb)
    
    # Create a copy of the image for annotation
    annotated_image = image.copy()
    
    # List to store hand landmarks
    landmarks_list = []
    
    # If hands detected, draw landmarks and extract coordinates
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw the hand landmarks and connections
            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # Extract the landmarks coordinates
            landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
            landmarks_list.append(landmarks)
    
    return annotated_image, landmarks_list

def detect_hands_in_video(video_path, is_webcam=False):
    """Process video or webcam feed to detect hands. Yields frames with annotations."""
    # Initialize video capture
    cap = cv2.VideoCapture(0 if is_webcam else video_path)
    
    # Check if video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return
    
    while cap.isOpened():
        # Read a frame
        success, frame = cap.read()
        if not success:
            break
        
        # Process the frame
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = video_hands_model.process(image_rgb)
        
        landmarks_list = []
        
        # If hands detected, draw landmarks and extract coordinates
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the hand landmarks and connections
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Extract the landmarks coordinates
                landmarks = [(lm.x, lm.y, lm.z) for lm in hand_landmarks.landmark]
                landmarks_list.append(landmarks)
        
        # Yield the annotated frame and landmarks
        yield frame, landmarks_list
    
    # Release resources
    cap.release()