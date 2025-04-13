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
    initial_sidebar_state="collapsed"
)

# Custom CSS for Spotify-like styling
st.markdown("""
<style>
    /* Main background and text colors */
    .main {
        background-color: #121212;
        color: #FFFFFF;
    }
    .stApp {
        background-color: #121212;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Headers */
    h1 {
        color: #1DB954;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin-bottom: 24px;
    }
    h2, h3 {
        color: #FFFFFF;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    /* Container styling */
    .status-box {
        background-color: #181818;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        transition: background-color 0.3s;
    }
    .status-box:hover {
        background-color: #282828;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .status-indicator.playing {
        background-color: #1DB954;
        box-shadow: 0 0 8px #1DB954;
    }
    .status-indicator.paused {
        background-color: #FFC107;
        box-shadow: 0 0 8px #FFC107;
    }
    .status-indicator.stopped {
        background-color: #E91E63;
        box-shadow: 0 0 8px #E91E63;
    }
    
    /* Song info */
    .song-info {
        color: #B3B3B3;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 14px;
        margin-top: 8px;
    }
    
    /* Gesture display */
    .gesture-name {
        color: #1DB954;
        font-weight: 500;
    }
    .gesture-value {
        font-size: 28px;
        font-weight: 700;
        color: #1DB954;
        letter-spacing: -0.04em;
    }
    
    /* Control buttons - make Spotify-like */
    .stButton>button {
        background-color: #282828;
        color: #FFFFFF;
        border-radius: 50%;
        width: 48px;
        height: 48px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        transition: transform 0.2s, background-color 0.2s;
        font-size: 18px;
        padding: 0;
    }
    .stButton>button:hover {
        background-color: #333333;
        transform: scale(1.1);
    }
    .stButton>button:active {
        transform: scale(0.95);
    }
    
    /* Main play button */
    .play-button button {
        background-color: #1DB954;
        width: 56px;
        height: 56px;
        font-size: 22px;
    }
    .play-button button:hover {
        background-color: #1ED760;
    }
    
    /* Video container styling */
    .video-container {
        background-color: #000000;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #6A6A6A;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #282828;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 12px;
    }
    
    /* Gesture guide */
    .gesture-guide {
        background-color: #181818;
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
    }
    .gesture-guide-item {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
        padding: 8px;
        border-radius: 6px;
        transition: background-color 0.2s;
    }
    .gesture-guide-item:hover {
        background-color: #282828;
    }
    .gesture-emoji {
        font-size: 24px;
        margin-right: 12px;
        min-width: 40px;
        text-align: center;
    }
    .gesture-description {
        color: #FFFFFF;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }
    .gesture-action {
        color: #1DB954;
        font-weight: 500;
        margin-left: 6px;
    }
    
    /* Progress bar (for potential future implementation) */
    .progress-container {
        background-color: #535353;
        height: 4px;
        border-radius: 2px;
        margin: 12px 0;
        position: relative;
    }
    .progress-bar {
        background-color: #1DB954;
        height: 4px;
        border-radius: 2px;
        width: 30%;
    }
    .progress-bar:hover {
        background-color: #1ED760;
    }
    .progress-time {
        display: flex;
        justify-content: space-between;
        color: #B3B3B3;
        font-size: 12px;
        margin-top: 6px;
    }
    
    /* Song list */
    .song-list-item {
        display: flex;
        align-items: center;
        padding: 10px;
        border-radius: 6px;
        transition: background-color 0.2s;
    }
    .song-list-item:hover {
        background-color: #282828;
        cursor: pointer;
    }
    .song-number {
        color: #B3B3B3;
        margin-right: 12px;
        min-width: 20px;
    }
    .song-title {
        color: #FFFFFF;
    }
    .current-song {
        color: #1DB954;
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

# Application header with Spotify-style branding
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 24px;">
    <div style="font-size: 32px; margin-right: 12px;">🎵</div>
    <div>
        <h1 style="margin-bottom: 0;">Gesture-Controlled Player</h1>
        <div style="color: #B3B3B3; margin-top: 0;">Control your music with hand gestures</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create layout columns with better proportions
col1, col2 = st.columns([5, 3])

# Main content column with video feed and song list
with col1:
    # Camera feed in Spotify-style container
    st.markdown('<h2>Camera Feed</h2>', unsafe_allow_html=True)
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    video_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Song library section
    st.markdown('<h2 style="margin-top: 32px;">Your Library</h2>', unsafe_allow_html=True)
    
    # Show available songs
    songs = load_songs()
    if len(songs) > 0:
        song_list = st.container()
        with song_list:
            st.markdown('<div class="status-box">', unsafe_allow_html=True)
            for i, song in enumerate(songs):
                song_name = os.path.basename(song)
                current_class = "current-song" if i == st.session_state.current_song_index and st.session_state.current_status != "stopped" else ""
                st.markdown(f"""
                <div class="song-list-item" onclick="alert('Song clicked!')">
                    <div class="song-number">{i+1}</div>
                    <div class="song-title {current_class}">{song_name}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-box" style="text-align: center; padding: 32px;">
            <div style="font-size: 48px; margin-bottom: 16px;">🎵</div>
            <div style="font-weight: 600; margin-bottom: 8px;">No songs found</div>
            <div style="color: #B3B3B3; font-size: 14px;">Add .mp3 or .wav files to your 'songs' folder</div>
        </div>
        """, unsafe_allow_html=True)

# Control panel column
with col2:
    # Now Playing status with Spotify-style
    st.markdown('<h2>Now Playing</h2>', unsafe_allow_html=True)
    now_playing_container = st.container()
    
    with now_playing_container:
        st.markdown(f"""
        <div class="status-box">
            <div style="display: flex; align-items: center;">
                <div style="width: 64px; height: 64px; background-color: #333; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                    <div style="font-size: 24px;">🎵</div>
                </div>
                <div style="flex-grow: 1;">
                    <div style="font-size: 18px; font-weight: 700; margin-bottom: 4px;">
                        {st.session_state.current_song if st.session_state.current_song != "No song playing" else "Not Playing"}
                    </div>
                    <div style="color: #B3B3B3; font-size: 14px;">
                        Gesture Media Player
                    </div>
                </div>
                <div>
                    <span class="status-indicator {st.session_state.current_status}"></span>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-bar"></div>
            </div>
            <div class="progress-time">
                <div>0:00</div>
                <div>3:45</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Manual controls with Spotify styling
    st.markdown('<h2>Controls</h2>', unsafe_allow_html=True)
    st.markdown('<div class="status-box">', unsafe_allow_html=True)
    
    controls_col1, controls_col2, controls_col3, controls_col4, controls_col5 = st.columns([1, 1, 1.2, 1, 1])
    
    with controls_col1:
        if st.button("⏮️", key="previous", help="Previous Song"):
            previous_song()
    
    with controls_col2:
        if st.button("⏸️", key="pause", help="Pause"):
            pause_song()
    
    with controls_col3:
        st.markdown('<div class="play-button">', unsafe_allow_html=True)
        if st.button("▶️", key="play", help="Play/Resume"):
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy() and st.session_state.current_status == "paused":
                unpause_song()
            else:
                play_song(st.session_state.current_song_index)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with controls_col4:
        if st.button("⏹️", key="stop", help="Stop"):
            stop_song()
    
    with controls_col5:
        if st.button("⏭️", key="next", help="Next Song"):
            next_song()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current gesture with improved styling
    st.markdown('<h2>Detected Gesture</h2>', unsafe_allow_html=True)
    gesture_container = st.container()
    
    with gesture_container:
        st.markdown(f"""
        <div class="status-box" style="text-align: center; padding: 20px;">
            <div style="font-size: 48px; margin-bottom: 10px;">
                {
                "👐" if st.session_state.current_gesture == "play" else
                "✊" if st.session_state.current_gesture == "pause" else
                "🖐️" if st.session_state.current_gesture == "stop" else
                "✌️" if st.session_state.current_gesture == "next" else
                "👆" if st.session_state.current_gesture == "previous" else
                "👋"
                }
            </div>
            <div class="gesture-value">{st.session_state.current_gesture.capitalize()}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gesture Guide with improved styling
    st.markdown('<h2>Gesture Guide</h2>', unsafe_allow_html=True)
    with st.container():
        st.markdown("""
        <div class="gesture-guide">
            <div class="gesture-guide-item">
                <div class="gesture-emoji">👐</div>
                <div class="gesture-description">Open Palm <span class="gesture-action">Play/Resume</span></div>
            </div>
            <div class="gesture-guide-item">
                <div class="gesture-emoji">✊</div>
                <div class="gesture-description">Closed Fist <span class="gesture-action">Pause</span></div>
            </div>
            <div class="gesture-guide-item">
                <div class="gesture-emoji">🖐️</div>
                <div class="gesture-description">Palm Down <span class="gesture-action">Stop</span></div>
            </div>
            <div class="gesture-guide-item">
                <div class="gesture-emoji">✌️</div>
                <div class="gesture-description">Peace Sign <span class="gesture-action">Next Song</span></div>
            </div>
            <div class="gesture-guide-item">
                <div class="gesture-emoji">👆</div>
                <div class="gesture-description">Index Finger <span class="gesture-action">Previous Song</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Spotify-style footer
st.markdown("""
<div class="footer">
    <p>Gesture-Controlled Media Player © 2025 • Made with ❤️</p>
</div>
""", unsafe_allow_html=True)

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
            
            # Update the Now Playing display
            now_playing_container.markdown(f"""
            <div class="status-box">
                <div style="display: flex; align-items: center;">
                    <div style="width: 64px; height: 64px; background-color: #333; border-radius: 6px; display: flex; align-items: center; justify-content: center; margin-right: 16px;">
                        <div style="font-size: 24px;">🎵</div>
                    </div>
                    <div style="flex-grow: 1;">
                        <div style="font-size: 18px; font-weight: 700; margin-bottom: 4px;">
                            {st.session_state.current_song if st.session_state.current_song != "No song playing" else "Not Playing"}
                        </div>
                        <div style="color: #B3B3B3; font-size: 14px;">
                            Gesture Media Player
                        </div>
                    </div>
                    <div>
                        <span class="status-indicator {st.session_state.current_status}"></span>
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar"></div>
                </div>
                <div class="progress-time">
                    <div>0:00</div>
                    <div>3:45</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Update gesture display
            gesture_container.markdown(f"""
            <div class="status-box" style="text-align: center; padding: 20px;">
                <div style="font-size: 48px; margin-bottom: 10px;">
                    {
                    "👐" if st.session_state.current_gesture == "play" else
                    "✊" if st.session_state.current_gesture == "pause" else
                    "🖐️" if st.session_state.current_gesture == "stop" else
                    "✌️" if st.session_state.current_gesture == "next" else
                    "👆" if st.session_state.current_gesture == "previous" else
                    "👋"
                    }
                </div>
                <div class="gesture-value">{st.session_state.current_gesture.capitalize()}</div>
            </div>
            """, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error with video capture: {e}")
        video_placeholder.error("Camera access error. Please check your webcam connection and permissions.")

# Run the video processing
process_video()