# app.py
import streamlit as st
import cv2
import tempfile
import os
import numpy as np
import time
import pyautogui  # For sending keyboard shortcuts to VLC
from PIL import Image
from mediapipe_utils import detect_hands_in_image, detect_hands_in_video
from media_controls import map_gesture_to_action, get_finger_states

# Configure Streamlit page
st.set_page_config(page_title="Gesture Control Media Player", layout="wide")

st.markdown("""
    <style>
        .main {background-color: #fafafa;}
        h1, h2, h3 {color: #303030;}
        .stButton>button {
            border-radius: 8px;
            background-color: #4CAF50;
            color: white;
        }
        .status-box {
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin: 10px 0;
        }
        .playing {
            background-color: #4CAF50;
            color: white;
        }
        .paused {
            background-color: #FFC107;
            color: black;
        }
        .stopped {
            background-color: #F44336;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🖐️ Gesture Control Media Player")
st.markdown("Use hand gestures to control your VLC media player that's playing on your laptop.")

# Sidebar options
option = st.sidebar.radio(
    "Choose Input Type",
    ["📷 Single Image", "🎦 Webcam Live Feed", "🎬 Video File", "📁 Image Folder"]
)

st.sidebar.markdown("""
### Gesture Instructions:
- 🖐️ Open hand (all fingers up) = Play
- ✊ Closed fist (all fingers down) = Pause
- 👇 Palm facing down = Stop
- ✌️ Peace sign (index + middle up) = Next song
- ☝️ Index finger only up = Previous song
""")

# ========== Media Player Functions ==========
def initialize_player():
    """Initialize the player state in session state"""
    if 'player_state' not in st.session_state:
        st.session_state.player_state = "stopped"  # Options: playing, paused, stopped
    if 'current_song' not in st.session_state:
        st.session_state.current_song = None
    if 'last_action_time' not in st.session_state:
        st.session_state.last_action_time = 0
    if 'last_action' not in st.session_state:
        st.session_state.last_action = None

def perform_media_action(action):
    """Send keyboard shortcuts to control VLC media player"""
    # Debounce actions - only allow one action every 1 second
    current_time = time.time()
    
    # Skip if it's the same action as before and too soon
    if action == st.session_state.last_action and current_time - st.session_state.last_action_time < 1:
        return False
    
    # Update the last action time and action
    st.session_state.last_action_time = current_time
    st.session_state.last_action = action
    
    if action == "play":
        # If already playing, don't do anything
        if st.session_state.player_state == "playing":
            return False
            
        # Space bar toggles play/pause in VLC
        pyautogui.press('space')
        st.session_state.player_state = "playing"
        return True
    
    elif action == "pause":
        # If already paused, don't do anything
        if st.session_state.player_state == "paused":
            return False
            
        # Space bar toggles play/pause in VLC
        pyautogui.press('space')
        st.session_state.player_state = "paused"
        return True
    
    elif action == "stop":
        # If already stopped, don't do anything
        if st.session_state.player_state == "stopped":
            return False
            
        # 's' key stops media in VLC
        pyautogui.press('s')
        st.session_state.player_state = "stopped"
        return True
    
    elif action == "next":
        # 'n' key plays next track in VLC
        pyautogui.press('n')
        if st.session_state.current_song:
            st.session_state.current_song = f"Next after {st.session_state.current_song}"
        return True
    
    elif action == "previous":
        # 'p' key plays previous track in VLC
        pyautogui.press('p')
        if st.session_state.current_song:
            st.session_state.current_song = f"Previous before {st.session_state.current_song}"
        return True
    
    return False

# Initialize player
initialize_player()

# Display current player state function
def show_player_status():
    if st.session_state.player_state == "playing":
        st.markdown('<div class="status-box playing">▶️ PLAYING</div>', unsafe_allow_html=True)
    elif st.session_state.player_state == "paused":
        st.markdown('<div class="status-box paused">⏸️ PAUSED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box stopped">⏹️ STOPPED</div>', unsafe_allow_html=True)
    
    # If there's a current song, display it
    if st.session_state.current_song:
        st.markdown(f"**Current Song:** {st.session_state.current_song}")

# Important note about VLC control
st.info("⚠️ This app sends keyboard shortcuts to control VLC. Make sure VLC is the active window when using gestures.", icon="ℹ️")

# ========== Single Image Mode ==========
if option == "📷 Single Image":
    st.header("Hand Gesture Detection from Image")
    
    # Display player status
    status_placeholder = st.empty()
    status_placeholder.markdown(
        f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
        {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
        unsafe_allow_html=True
    )
    
    # Current song display
    song_placeholder = st.empty()
    if st.session_state.current_song:
        song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
    
    uploaded_img = st.file_uploader("Upload an image with a hand gesture", type=["png", "jpg", "jpeg"])
    
    if uploaded_img:
        # Create columns for showing original and processed images side by side
        col1, col2 = st.columns(2)
        
        # Read and process the image
        file_bytes = uploaded_img.read()
        np_img = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), 1)
        result_img, landmarks = detect_hands_in_image(np_img)
        
        # Display original image
        with col1:
            st.image(cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB), caption="Original Image")
        
        # Display processed image with landmarks
        with col2:
            st.image(result_img, channels="BGR", caption="Detected Hand Landmarks")
        
        # Analyze gesture and display result
        if landmarks:
            # Get the gesture and corresponding action
            finger_states = get_finger_states(landmarks[0])
            action = map_gesture_to_action(landmarks)
            
            # Display finger state visualization
            st.markdown("### Detected Hand Gesture")
            finger_names = ["👍 Thumb", "☝️ Index", "🖕 Middle", "💍 Ring", "🤙 Pinky"]
            
            # Create a visual representation of finger states
            cols = st.columns(5)
            for i, (finger, state) in enumerate(zip(finger_names, finger_states)):
                with cols[i]:
                    if state:
                        st.markdown(f"<div style='text-align:center;color:green;'>{finger}<br>UP</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='text-align:center;color:red;'>{finger}<br>DOWN</div>", unsafe_allow_html=True)
            
            # Display the detected action
            action_placeholder = st.empty()
            if action:
                action_placeholder.success(f"### Detected Action: **{action.upper()}**")
                
                # Automatically apply the action - no button needed
                if perform_media_action(action):
                    # Update status display after action
                    status_placeholder.markdown(
                        f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
                        {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
                        unsafe_allow_html=True
                    )
                    
                    # Update song display if needed
                    if st.session_state.current_song:
                        song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
            else:
                action_placeholder.warning("No specific gesture action detected")
        else:
            st.warning("No hand landmarks detected in the image")

# ========== Webcam Mode ==========
elif option == "🎦 Webcam Live Feed":
    st.header("Live Webcam Gesture Detection")
    
    # Initialize webcam state
    if 'webcam_active' not in st.session_state:
        st.session_state.webcam_active = False
    
    # Display player status
    status_placeholder = st.empty()
    status_placeholder.markdown(
        f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
        {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
        unsafe_allow_html=True
    )
    
    # Current song display
    song_placeholder = st.empty()
    if st.session_state.current_song:
        song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
    
    # Current action display
    action_placeholder = st.empty()
    
    # Frame placeholder
    frame_placeholder = st.empty()
    
    # Remind about VLC window
    st.warning("Make sure VLC is the active window while controlling with gestures")

    # Start/Stop buttons
    col1, col2 = st.columns(2)
    with col1:
        if not st.session_state.webcam_active:
            if st.button("▶️ Start Webcam", type="primary", use_container_width=True):
                st.session_state.webcam_active = True
                st.rerun()
    with col2:
        if st.session_state.webcam_active:
            if st.button("⏹️ Stop Webcam", type="secondary", use_container_width=True):
                st.session_state.webcam_active = False
                st.rerun()
    
    # Webcam processing when active
    if st.session_state.webcam_active:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        try:
            while st.session_state.webcam_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to capture frame from webcam")
                    break
                
                # Flip frame for mirror effect (like selfie camera)
                frame = cv2.flip(frame, 1)
                
                # Process frame to detect hands
                annotated_frame, landmarks = detect_hands_in_image(frame)
                
                # Get action from landmarks
                action = None
                if landmarks:
                    action = map_gesture_to_action(landmarks)
                    
                    # Apply the action to media player automatically
                    if action and perform_media_action(action):
                        # Update status
                        status_placeholder.markdown(
                            f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
                            {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
                            unsafe_allow_html=True
                        )
                        
                        # Update song display if needed
                        if st.session_state.current_song:
                            song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
                
                # Show action text
                if action:
                    action_placeholder.markdown(f"<h3>Detected: {action.upper()}</h3>", unsafe_allow_html=True)
                else:
                    action_placeholder.markdown("<h3>No gesture detected</h3>", unsafe_allow_html=True)
                
                # Display the frame (like mobile camera preview)
                frame_placeholder.image(annotated_frame, channels="BGR", caption="Live Webcam Feed")
                
                # Small delay for smooth video
                time.sleep(0.03)  # ~30 FPS
                
                # Check if we should still be active
                if not st.session_state.webcam_active:
                    break
                    
        finally:
            cap.release()
            frame_placeholder.empty()  # Clear the frame when stopped
            action_placeholder.empty()  # Clear the action text

# ========== Video File Mode ==========
elif option == "🎬 Video File":
    st.header("Video File Gesture Detection")
    
    # Display player status
    status_placeholder = st.empty()
    status_placeholder.markdown(
        f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
        {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
        unsafe_allow_html=True
    )
    
    # Current song display
    song_placeholder = st.empty()
    if st.session_state.current_song:
        song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
    
    uploaded_video = st.file_uploader("Upload a video with hand gestures", type=["mp4", "mov", "avi"])
    
    # Remind about VLC window
    st.warning("Make sure VLC is the active window while processing video gestures")
    
    if uploaded_video:
        # Save the uploaded video to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(uploaded_video.read())
        temp_file.close()
        
        # Video processing options
        st.subheader("Video Processing")
        
        if st.button("Process Video"):
            # Process the video
            cap = cv2.VideoCapture(temp_file.name)
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create a progress bar
            progress_bar = st.progress(0)
            
            # Status display
            status_placeholder = st.empty()
            action_placeholder = st.empty()
            frame_placeholder = st.empty()
            
            # Process each frame
            frame_index = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process every 5th frame for better performance
                if frame_index % 5 == 0:
                    # Process frame to detect hands
                    annotated_frame, landmarks = detect_hands_in_image(frame)
                    
                    # Get action from landmarks
                    action = None
                    if landmarks:
                        action = map_gesture_to_action(landmarks)
                        
                        # Apply the action to media player automatically
                        if action and perform_media_action(action):
                            # Update status
                            status_placeholder.markdown(
                                f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
                                {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
                                unsafe_allow_html=True
                            )
                            
                            # Update song display if needed
                            if st.session_state.current_song:
                                song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
                    
                    # Show action text
                    if action:
                        action_placeholder.markdown(f"<h3>Detected: {action.upper()}</h3>", unsafe_allow_html=True)
                    else:
                        action_placeholder.markdown("<h3>No gesture detected</h3>", unsafe_allow_html=True)
                    
                    # Display the frame
                    frame_placeholder.image(annotated_frame, channels="BGR", caption=f"Video Frame {frame_index}")
                    
                    # Update progress
                    progress_bar.progress(min(1.0, frame_index / frame_count))
                
                frame_index += 1
                
                # Simulate real-time playback (slower to see the effects)
                time.sleep(2/fps)  # Slowed down for better visualization
            
            # Clean up
            cap.release()
            os.unlink(temp_file.name)
            
            st.success("Video processing complete!")

# ========== Image Folder Mode ==========
elif option == "📁 Image Folder":
    st.header("Process Multiple Images")
    
    # Display player status
    status_placeholder = st.empty()
    status_placeholder.markdown(
        f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
        {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
        unsafe_allow_html=True
    )
    
    # Current song display
    song_placeholder = st.empty()
    if st.session_state.current_song:
        song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
    
    # Remind about VLC window
    st.warning("Make sure VLC is the active window while processing image gestures")
    
    st.info("In a desktop application, you would select a folder. For this web demo, please upload multiple images individually.")
    
    uploaded_files = st.file_uploader("Upload multiple images with hand gestures", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if uploaded_files:
        process_button = st.button("Process All Images")
        
        if process_button:
            st.subheader("Processing Results")
            
            for i, uploaded_file in enumerate(uploaded_files):
                st.markdown(f"### Image {i+1}: {uploaded_file.name}")
                
                # Read and process the image
                file_bytes = uploaded_file.read()
                np_img = cv2.imdecode(np.frombuffer(file_bytes, np.uint8), 1)
                result_img, landmarks = detect_hands_in_image(np_img)
                
                # Create columns for showing original and processed images
                col1, col2 = st.columns(2)
                
                # Display original image
                with col1:
                    st.image(cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB), caption="Original Image")
                
                # Display processed image with landmarks
                with col2:
                    st.image(result_img, channels="BGR", caption="Detected Hand Landmarks")
                
                # Analyze gesture and display result
                if landmarks:
                    # Get the gesture and corresponding action
                    finger_states = get_finger_states(landmarks[0])
                    action = map_gesture_to_action(landmarks)
                    
                    # Display the detected action
                    if action:
                        st.success(f"Detected Action: **{action.upper()}**")
                        
                        # Automatically apply the action to the media player
                        if perform_media_action(action):
                            # Update status
                            status_placeholder.markdown(
                                f"""<div class="status-box {'playing' if st.session_state.player_state == 'playing' else 'paused' if st.session_state.player_state == 'paused' else 'stopped'}">
                                {'▶️ PLAYING' if st.session_state.player_state == 'playing' else '⏸️ PAUSED' if st.session_state.player_state == 'paused' else '⏹️ STOPPED'}</div>""", 
                                unsafe_allow_html=True
                            )
                            
                            # Update song display if needed
                            if st.session_state.current_song:
                                song_placeholder.markdown(f"**Current Song:** {st.session_state.current_song}")
                        
                        # Delay to see the effect
                        time.sleep(2)
                    else:
                        st.warning("No specific gesture action detected")
                else:
                    st.warning("No hand landmarks detected in the image")
                
                # Show current player state after processing this image
                state_text = "▶️ PLAYING" if st.session_state.player_state == "playing" else "⏸️ PAUSED" if st.session_state.player_state == "paused" else "⏹️ STOPPED"
                st.info(f"Player state after this image: {state_text}")
                
                # Add a separator between images
                if i < len(uploaded_files) - 1:
                    st.markdown("---")