import streamlit as st
import cv2
import time
import os
import pygame
import threading
import numpy as np
from media_controls import map_gesture_to_action, detect_hands_in_video

# Set page configuration
st.set_page_config(
    page_title="Gesture-Controlled Media Player",
    page_icon="🎵",
    layout="wide",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background-color: #1E1E1E;
        color: white;
    }
    .css-18e3th9 {
        padding-top: 2rem;
    }
    .stApp {
        background-color: #1E1E1E;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #4FC3F7;
    }
    .status-box {
        background-color: #2C2C2C;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .status-indicator {
        display: inline-block;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .status-indicator.playing {
        background-color: #4CAF50;
    }
    .status-indicator.paused {
        background-color: #FF9800;
    }
    .status-indicator.stopped {
        background-color: #F44336;
    }
    .song-info {
        color: #90CAF9;
        font-style: italic;
        margin-top: 5px;
    }
    .gesture-name {
        color: #FFAB40;
        font-weight: 500;
    }
    .gesture-value {
        font-size: 24px;
        font-weight: 500;
        color: #FFAB40;
    }
    .control-button {
        margin: 0 5px;
    }
    .footer {
        text-align: center;
        color: #777;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state if it doesn't exist
if 'current_song_index' not in st.session_state:
    st.session_state.current_song_index = 0
    st.session_state.current_status = "stopped"
    st.session_state.current_song = "No song playing"
    st.session_state.current_gesture = "None"
    st.session_state.has_songs = False
    st.session_state.initialized = False

# Initialize pygame for audio
def initialize_pygame():
    if not st.session_state.initialized:
        pygame.init()
        pygame.mixer.init()
        st.session_state.initialized = True

# Load songs from directory
def load_songs():
    song_folder = "songs"
    if not os.path.exists(song_folder):
        os.makedirs(song_folder)
    songs = [os.path.join(song_folder, f) for f in os.listdir(song_folder) if f.endswith(('.mp3', '.wav'))]
    st.session_state.songs = songs
    st.session_state.has_songs = len(songs) > 0
    return songs

# Music control functions
def play_song(index):
    initialize_pygame()
    
    if not st.session_state.has_songs:
        return
    
    st.session_state.current_song_index = index % len(st.session_state.songs)
    pygame.mixer.music.load(st.session_state.songs[st.session_state.current_song_index])
    pygame.mixer.music.play()
    st.session_state.current_status = "playing"
    st.session_state.current_song = os.path.basename(st.session_state.songs[st.session_state.current_song_index])

def pause_song():
    initialize_pygame()
    pygame.mixer.music.pause()
    st.session_state.current_status = "paused"

def unpause_song():
    initialize_pygame()
    pygame.mixer.music.unpause()
    st.session_state.current_status = "playing"

def stop_song():
    initialize_pygame()
    pygame.mixer.music.stop()
    st.session_state.current_status = "stopped"

def next_song():
    if not st.session_state.has_songs:
        return
        
    st.session_state.current_song_index = (st.session_state.current_song_index + 1) % len(st.session_state.songs)
    play_song(st.session_state.current_song_index)

def previous_song():
    if not st.session_state.has_songs:
        return
        
    st.session_state.current_song_index = (st.session_state.current_song_index - 1) % len(st.session_state.songs)
    play_song(st.session_state.current_song_index)

# Application header
st.title("Gesture-Controlled Media Player")
st.markdown("Control your music with hand gestures! 👋")

# Create layout columns
col1, col2 = st.columns([3, 2])

# Main video feed and controls
with col1:
    # Camera feed
    st.subheader("Camera Feed")
    video_placeholder = st.empty()

# Status and controls column
with col2:
    # Playback status
    st.subheader("Playback Status")
    status_container = st.container()
    
    with status_container:
        st.markdown(f"""
        <div class="status-box">
            <div>
                <span class="status-indicator {st.session_state.current_status}"></span>
                <span style="font-size: 18px; font-weight: 500;">{st.session_state.current_status.capitalize()}</span>
            </div>
            <div class="song-info">{st.session_state.current_song}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Manual controls
    st.subheader("Manual Controls")
    controls_col1, controls_col2, controls_col3, controls_col4, controls_col5 = st.columns(5)
    
    with controls_col1:
        if st.button("⏮️", key="previous", help="Previous Song"):
            previous_song()
    
    with controls_col2:
        if st.button("▶️", key="play", help="Play/Resume"):
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy() and st.session_state.current_status == "paused":
                unpause_song()
            else:
                play_song(st.session_state.current_song_index)
    
    with controls_col3:
        if st.button("⏸️", key="pause", help="Pause"):
            pause_song()
    
    with controls_col4:
        if st.button("⏹️", key="stop", help="Stop"):
            stop_song()
    
    with controls_col5:
        if st.button("⏭️", key="next", help="Next Song"):
            next_song()
    
    # Current gesture
    st.subheader("Detected Gesture")
    gesture_container = st.container()
    
    with gesture_container:
        st.markdown(f"""
        <div class="status-box">
            <div class="gesture-value">{st.session_state.current_gesture.capitalize()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gesture Guide
    st.subheader("Gesture Guide")
    with st.container():
        st.markdown("""
        <div class="status-box">
            <ul style="list-style-type: none; padding-left: 0;">
                <li style="margin-bottom: 10px;"><span class="gesture-name">👐 Open Palm (all fingers up):</span> Play/Resume</li>
                <li style="margin-bottom: 10px;"><span class="gesture-name">✊ Closed Fist (all fingers down):</span> Pause</li>
                <li style="margin-bottom: 10px;"><span class="gesture-name">🖐️ Palm Down (3+ fingers extended):</span> Stop</li>
                <li style="margin-bottom: 10px;"><span class="gesture-name">✌️ Peace Sign (index & middle up):</span> Next Song</li>
                <li style="margin-bottom: 10px;"><span class="gesture-name">👆 Index Finger Only:</span> Previous Song</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    <p>Gesture-Controlled Media Player © 2025</p>
</div>
""", unsafe_allow_html=True)

# Load songs at start
songs = load_songs()

# Set up video capture and processing
def process_video():
    # Initialize variables for gesture handling
    last_action = None
    cooldown = 2  # seconds
    last_time = time.time()
    
    # Start video capture
    try:
        for frame, landmarks in detect_hands_in_video(video_path=None, is_webcam=True):
            action = map_gesture_to_action(landmarks)
            
            # Update current gesture for display
            if action is not None:
                st.session_state.current_gesture = action
            
            # Only act if cooldown passed
            if action != last_action and action is not None and (time.time() - last_time > cooldown):
                last_time = time.time()
                last_action = action
                
                # Control the music based on the detected gesture
                if action == "play":
                    if pygame.mixer.get_init() and pygame.mixer.music.get_busy() and st.session_state.current_status == "paused":
                        unpause_song()
                    else:
                        play_song(st.session_state.current_song_index)
                elif action == "pause":
                    pause_song()
                elif action == "stop":
                    stop_song()
                elif action == "next":
                    next_song()
                elif action == "previous":
                    previous_song()
            
            # Convert to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
            
            # Update the status display
            status_container.markdown(f"""
            <div class="status-box">
                <div>
                    <span class="status-indicator {st.session_state.current_status}"></span>
                    <span style="font-size: 18px; font-weight: 500;">{st.session_state.current_status.capitalize()}</span>
                </div>
                <div class="song-info">{st.session_state.current_song}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Update gesture display
            gesture_container.markdown(f"""
            <div class="status-box">
                <div class="gesture-value">{st.session_state.current_gesture.capitalize()}</div>
            </div>
            """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error with video capture: {e}")
        video_placeholder.error("Camera access error. Please check your webcam connection and permissions.")

# Run the video processing
process_video()