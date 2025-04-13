import streamlit as st
import cv2
import time
import os
import pygame
import numpy as np
from media_controls import map_gesture_to_action, detect_hands_in_video

# Set page configuration
st.set_page_config(
    page_title="Gesture-Controlled Media Player",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced Spotify-like styling with animations
st.markdown("""
<style>
    /* Main background and text colors */
    .main {
        background: linear-gradient(to bottom, #121212, #181818);
        color: #FFFFFF;
    }
    .stApp {
        background: linear-gradient(to bottom, #121212, #181818);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
    }
    
    /* Headers with animations */
    h1 {
        color: #1DB954;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin-bottom: 24px;
        animation: fadeInDown 0.8s ease-out;
        text-shadow: 0 0 15px rgba(29, 185, 84, 0.4);
    }
    h2, h3 {
        color: #FFFFFF;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: -0.04em;
        margin-top: 20px;
        margin-bottom: 15px;
        animation: fadeInLeft 0.6s ease-out;
    }
    
    /* Container styling with animations */
    .status-box {
        background-color: #181818;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
        animation: fadeIn 0.8s ease-out;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .status-box:hover {
        background-color: #282828;
        transform: translateY(-5px);
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.6);
    }
    
    /* Enhanced status indicators with pulse animations */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 10px;
        position: relative;
    }
    .status-indicator.playing {
        background-color: #1DB954;
        box-shadow: 0 0 8px #1DB954;
        animation: pulse 1.5s infinite;
    }
    .status-indicator.paused {
        background-color: #FFC107;
        box-shadow: 0 0 8px #FFC107;
    }
    .status-indicator.stopped {
        background-color: #E91E63;
        box-shadow: 0 0 8px #E91E63;
    }
    
    /* Status bar animation */
    .playing-status-bar {
        display: flex;
        gap: 3px;
        align-items: center;
        margin-top: 6px;
        height: 20px;
    }
    .status-bar {
        width: 4px;
        background-color: #1DB954;
        border-radius: 2px;
    }
    .status-bar:nth-child(1) { height: 12px; animation: sound-wave 1.2s infinite ease-in-out 0.0s; }
    .status-bar:nth-child(2) { height: 16px; animation: sound-wave 1.2s infinite ease-in-out 0.1s; }
    .status-bar:nth-child(3) { height: 10px; animation: sound-wave 1.2s infinite ease-in-out 0.2s; }
    .status-bar:nth-child(4) { height: 14px; animation: sound-wave 1.2s infinite ease-in-out 0.3s; }
    .status-bar:nth-child(5) { height: 18px; animation: sound-wave 1.2s infinite ease-in-out 0.4s; }
    
    /* Enhanced song info */
    .song-info {
        color: #B3B3B3;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 14px;
        margin-top: 12px;
        animation: fadeIn 1s ease-out;
        display: flex;
        align-items: center;
    }
    .song-info-details {
        margin-left: 12px;
    }
    .song-title-display {
        color: white;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 320px;
    }
    
    /* Album art placeholder */
    .album-art {
        width: 60px;
        height: 60px;
        background: linear-gradient(45deg, #282828, #383838);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        transition: transform 0.3s ease;
    }
    .album-art:hover {
        transform: scale(1.05);
    }
    
    /* Gesture display with animations */
    .gesture-name {
        color: #1DB954;
        font-weight: 500;
        animation: fadeIn 0.5s ease-out;
    }
    .gesture-value {
        font-size: 28px;
        font-weight: 700;
        color: #1DB954;
        letter-spacing: -0.04em;
        animation: pulse 2s infinite;
    }
    
    /* Enhanced control buttons with animations */
    .stButton>button {
        background-color: #282828;
        color: #FFFFFF;
        border-radius: 50%;
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: none;
        transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
        font-size: 20px;
        padding: 0;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4);
        margin: 0 auto;
    }
    .stButton>button:hover {
        background-color: #3A3A3A;
        transform: scale(1.15) translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
    }
    .stButton>button:active {
        transform: scale(0.95) translateY(2px);
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.3);
    }
    
    /* Enhanced main play button */
    .play-button button {
        background: linear-gradient(135deg, #1DB954, #1ED760);
        width: 70px;
        height: 70px;
        font-size: 26px;
        box-shadow: 0 8px 20px rgba(29, 185, 84, 0.4);
    }
    .play-button button:hover {
        background: linear-gradient(135deg, #1ED760, #1DB954);
        box-shadow: 0 12px 24px rgba(29, 185, 84, 0.6);
    }
    
    /* Enhanced webcam button */
    .webcam-button {
        display: inline-block;
        margin: 0 auto;
    }
    .webcam-button button {
        background: linear-gradient(to right, #1DB954, #1ED760);
        color: white;
        border-radius: 30px;
        padding: 12px 28px !important;
        width: auto;
        height: auto;
        font-weight: bold;
        font-size: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
        box-shadow: 0 8px 16px rgba(29, 185, 84, 0.4);
        border: none;
        outline: none;
        text-transform: uppercase;
        letter-spacing: 1px;
        animation: bounceIn 0.8s;
    }
    .webcam-button button:hover {
        background: linear-gradient(to right, #1ED760, #27F571);
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 12px 24px rgba(29, 185, 84, 0.6);
    }
    .webcam-button button:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: 0 4px 12px rgba(29, 185, 84, 0.4);
    }
    .webcam-icon {
        margin-right: 12px;
        font-size: 22px;
    }
    
    /* Enhanced video container */
    .video-container {
        background-color: #000000;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.6);
        transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1);
        border: 2px solid rgba(29, 185, 84, 0.3);
        animation: fadeIn 1s ease-out;
    }
    .video-container:hover {
        box-shadow: 0 16px 32px rgba(0, 0, 0, 0.7);
        border: 2px solid rgba(29, 185, 84, 0.6);
    }
    
    /* Enhanced camera placeholder */
    .camera-placeholder {
        background: linear-gradient(135deg, #181818, #222222);
        border-radius: 16px;
        padding: 40px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        height: 360px;
        animation: pulseOpacity 3s infinite;
    }
    .camera-icon {
        font-size: 80px;
        margin-bottom: 24px;
        color: #535353;
        animation: bounce 2s infinite;
        text-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    .camera-text {
        color: #B3B3B3;
        font-size: 20px;
        max-width: 260px;
        line-height: 1.5;
    }
    
    /* Enhanced footer */
    .footer {
        text-align: center;
        color: #6A6A6A;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #282828;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 12px;
        animation: fadeIn 1.5s ease-out;
    }
    .footer-logo {
        font-size: 18px;
        margin-bottom: 8px;
        animation: spin 8s linear infinite;
        display: inline-block;
    }
    
    /* Enhanced gesture guide */
    .gesture-guide {
        background: linear-gradient(135deg, #181818, #222222);
        border-radius: 12px;
        padding: 20px;
        margin-top: 16px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        animation: fadeIn 1s ease-out;
    }
    .gesture-guide-item {
        display: flex;
        align-items: center;
        margin-bottom: 16px;
        padding: 10px;
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
        border-left: 3px solid transparent;
    }
    .gesture-guide-item:hover {
        background-color: #282828;
        transform: translateX(5px);
        border-left: 3px solid #1DB954;
    }
    .gesture-emoji {
        font-size: 28px;
        margin-right: 16px;
        min-width: 50px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .gesture-guide-item:hover .gesture-emoji {
        transform: scale(1.2);
    }
    .gesture-description {
        color: #FFFFFF;
        font-family: 'Circular', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 15px;
    }
    .gesture-action {
        color: #1DB954;
        font-weight: 500;
        margin-left: 6px;
    }
    
    /* Enhanced song list */
    .song-list-item {
        display: flex;
        align-items: center;
        padding: 12px 16px;
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.19, 1, 0.22, 1);
        margin-bottom: 4px;
        border-left: 3px solid transparent;
    }
    .song-list-item:hover {
        background-color: #282828;
        transform: translateX(5px);
        border-left: 3px solid #1DB954;
    }
    .song-number {
        color: #B3B3B3;
        margin-right: 16px;
        min-width: 24px;
        font-weight: 500;
    }
    .song-title {
        color: #FFFFFF;
        font-weight: 400;
    }
    .current-song {
        color: #1DB954;
        font-weight: 600;
    }
    .song-list-item.now-playing {
        background-color: rgba(29, 185, 84, 0.1);
        border-left: 3px solid #1DB954;
    }
    .now-playing-icon {
        margin-left: auto;
        color: #1DB954;
        animation: pulse 2s infinite;
    }
    
    /* Empty song list state */
    .empty-state {
        text-align: center;
        padding: 48px 32px;
        animation: fadeIn 1s ease-out;
    }
    .empty-state-icon {
        font-size: 64px;
        margin-bottom: 24px;
        animation: float 3s ease-in-out infinite;
    }
    .empty-state-title {
        font-weight: 600;
        font-size: 22px;
        margin-bottom: 12px;
        color: white;
    }
    .empty-state-text {
        color: #B3B3B3;
        font-size: 16px;
        max-width: 280px;
        margin: 0 auto;
        line-height: 1.5;
    }
    
    /* Volume control visualization */
    .volume-control {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 20px;
    }
    .volume-bar {
        width: 80%;
        height: 4px;
        background-color: #535353;
        border-radius: 2px;
        position: relative;
        overflow: hidden;
    }
    .volume-level {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 70%;
        background-color: #1DB954;
        border-radius: 2px;
    }
    .volume-knob {
        width: 12px;
        height: 12px;
        background-color: white;
        border-radius: 50%;
        position: absolute;
        top: 50%;
        left: 70%;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .volume-knob:hover {
        transform: translate(-50%, -50%) scale(1.2);
    }
    .volume-icon {
        font-size: 18px;
        margin-right: 10px;
        color: #B3B3B3;
    }
    
    /* New now playing card */
    .now-playing-card {
        background: linear-gradient(135deg, #252525, #1d1d1d);
        border-radius: 12px;
        padding: 20px;
        margin-top: 24px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        animation: fadeIn 0.8s;
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
        overflow: hidden;
    }
    .now-playing-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(to right, #1DB954, #1ED760, #1DB954);
        animation: progressBar 30s linear infinite;
    }
    .album-cover {
        width: 80px;
        height: 80px;
        background: linear-gradient(45deg, #535353, #383838);
        border-radius: 8px;
        margin-right: 20px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        flex-shrink: 0;
        animation: rotate 15s linear infinite;
        animation-play-state: paused;
    }
    .playing .album-cover {
        animation-play-state: running;
    }
    .song-details {
        flex-grow: 1;
    }
    .song-name {
        font-size: 18px;
        font-weight: 600;
        color: white;
        margin-bottom: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .song-artist {
        font-size: 14px;
        color: #B3B3B3;
    }
    
    /* Progress bar */
    .progress-container {
        margin-top: 12px;
        width: 100%;
    }
    .progress-bar {
        width: 100%;
        height: 4px;
        background-color: #535353;
        border-radius: 2px;
        overflow: hidden;
        cursor: pointer;
    }
    .progress-filled {
        height: 100%;
        background-color: #1DB954;
        border-radius: 2px;
        width: 30%;
        transition: width 1s linear;
    }
    .time-info {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #B3B3B3;
        margin-top: 6px;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInLeft {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); opacity: 1; }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); }
    }
    
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes pulseOpacity {
        0% { opacity: 0.8; }
        50% { opacity: 1; }
        100% { opacity: 0.8; }
    }
    
    @keyframes sound-wave {
        0% { height: 3px; }
        50% { height: 16px; }
        100% { height: 3px; }
    }
    
    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }
    
    @keyframes progressBar {
        0% { background-position: 0 0; }
        100% { background-position: 1200px 0; }
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .song-name {
            font-size: 16px;
        }
        .album-cover {
            width: 60px;
            height: 60px;
        }
        .stButton>button {
            width: 48px;
            height: 48px;
        }
        .play-button button {
            width: 60px;
            height: 60px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'current_song_index' not in st.session_state:
    st.session_state.current_song_index = 0
    st.session_state.current_status = "stopped"
    st.session_state.current_song = "No song playing"
    st.session_state.current_gesture = "None"
    st.session_state.has_songs = False
    st.session_state.initialized = False
    st.session_state.webcam_active = False
    st.session_state.volume = 70
    st.session_state.progress = 0
    st.session_state.last_update = time.time()

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
    st.session_state.progress = 0
    st.session_state.last_update = time.time()

def pause_song():
    initialize_pygame()
    pygame.mixer.music.pause()
    st.session_state.current_status = "paused"

def unpause_song():
    initialize_pygame()
    pygame.mixer.music.unpause()
    st.session_state.current_status = "playing"
    st.session_state.last_update = time.time()

def stop_song():
    initialize_pygame()
    pygame.mixer.music.stop()
    st.session_state.current_status = "stopped"
    st.session_state.progress = 0

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

# Set volume function
def set_volume(volume):
    initialize_pygame()
    pygame.mixer.music.set_volume(volume / 100)
    st.session_state.volume = volume

# Update progress bar
def update_progress():
    if st.session_state.current_status == "playing":
        # Simulate progress (real implementation would get actual song position)
        elapsed = time.time() - st.session_state.last_update
        # Assume average song length of 3 minutes
        song_length = 180
        progress_increment = (elapsed / song_length) * 100
        st.session_state.progress = min(st.session_state.progress + progress_increment, 100)
        st.session_state.last_update = time.time()
        
        # Auto-play next song when current one finishes
        if st.session_state.progress >= 100:
            next_song()

# Application header with enhanced Spotify-style branding
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 32px; animation: fadeInDown 0.8s;">
    <div style="font-size: 40px; margin-right: 16px; animation: pulse 3s infinite;">🎵</div>
    <div>
        <h1 style="margin-bottom: 0; font-size: 36px;">Gesture-Controlled Player</h1>
        <div style="color: #B3B3B3; margin-top: 4px; font-size: 16px;">Control your music with hand gestures</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create layout columns with better proportions
col1, col2 = st.columns([5, 3])

# Main content column with video feed and song list
with col1:
    # Camera feed section
    st.markdown('<h2>Camera Feed</h2>', unsafe_allow_html=True)
    
    # Enhanced video container
    st.markdown('<div class="video-container">', unsafe_allow_html=True)
    video_placeholder = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # If webcam is not active, show an enhanced placeholder with animations
    if not st.session_state.webcam_active:
        video_placeholder.markdown("""
        <div class="camera-placeholder">
            <div class="camera-icon">📹</div>
            <div class="camera-text">Click the button below to start the webcam and enable gesture controls</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Start/Stop webcam button with enhanced styling
    webcam_col1, webcam_col2, webcam_col3 = st.columns([1, 2, 1])
    with webcam_col2:
        st.markdown('<div style="text-align: center; margin: 24px 0;">', unsafe_allow_html=True)
        
        # Toggle button based on webcam state
        if not st.session_state.webcam_active:
            st.markdown('<div class="webcam-button">', unsafe_allow_html=True)
            if st.button("📹 Start", key="start_webcam"):
                st.session_state.webcam_active = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="webcam-button">', unsafe_allow_html=True)
            if st.button("⏹️ Stop", key="stop_webcam"):
                st.session_state.webcam_active = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Now Playing card - only show when a song is playing or paused
    if st.session_state.has_songs and st.session_state.current_status != "stopped":
        # Update progress for visual feedback
        update_progress()
        
        now_playing_class = "playing" if st.session_state.current_status == "playing" else ""
        song_name = os.path.basename(st.session_state.songs[st.session_state.current_song_index])
        song_artist = "Unknown Artist" # This would come from metadata in a real app
        
        st.markdown(f"""
        <div class="now-playing-card {now_playing_class}">
            <div class="album-cover">🎵</div>
            <div class="song-details">
                <div class="song-name">{song_name}</div>
                <div class="song-artist">{song_artist}</div>
                <div class="progress-container">
                    <div class="progress-bar">
                        <div class="progress-filled" style="width: {st.session_state.progress}%;"></div>
                    </div>
                    <div class="time-info">
                        <span>{int(st.session_state.progress * 180 / 100) // 60}:{int(st.session_state.progress * 180 / 100) % 60:02d}</span>
                        <span>3:00</span>
                    </div>
                </div>
                
                <div class="playing-status-bar" style="display: {'flex' if st.session_state.current_status == 'playing' else 'none'};">
                    <div class="status-bar"></div>
                    <div class="status-bar"></div>
                    <div class="status-bar"></div>
                    <div class="status-bar"></div>
                    <div class="status-bar"></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Song library section with enhanced styling
    st.markdown('<h2 style="margin-top: 32px;">Your Library</h2>', unsafe_allow_html=True)
    
    # Show available songs with enhanced visuals
    songs = load_songs()
    if len(songs) > 0:
        song_list = st.container()
        with song_list:
            st.markdown('<div class="status-box">', unsafe_allow_html=True)
            for i, song in enumerate(songs):
                song_name = os.path.basename(song)
                current_class = "current-song" if i == st.session_state.current_song_index and st.session_state.current_status != "stopped" else ""
                now_playing = "now-playing" if i == st.session_state.current_song_index and st.session_state.current_status != "stopped" else ""
                playing_icon = """<div class="now-playing-icon">♫</div>""" if i == st.session_state.current_song_index and st.session_state.current_status == "playing" else ""
                
                st.markdown(f"""
                <div class="song-list-item {now_playing}" onclick="alert('Song clicked!')">
                    <div class="song-number">{i+1}</div>
                    <div class="song-title {current_class}">{song_name}</div>
                    {playing_icon}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-box empty-state">
            <div class="empty-state-icon">🎵</div>
            <div class="empty-state-title">No songs found</div>
            <div class="empty-state-text">Add .mp3 or .wav files to your 'songs' folder to get started</div>
        </div>
        """, unsafe_allow_html=True)

# Control panel column with enhanced styling
with col2:
    # Current status display with enhanced visuals
    if st.session_state.has_songs and st.session_state.current_status != "stopped":
        st.markdown('<div class="status-box" style="margin-bottom: 24px;">', unsafe_allow_html=True)
        
        # Status indicator with proper styling based on state
        status_class = "playing" if st.session_state.current_status == "playing" else "paused"
        status_text = "Now Playing" if st.session_state.current_status == "playing" else "Paused"
        
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <div class="status-indicator {status_class}"></div>
            <div style="font-weight: 600; font-size: 18px;">{status_text}</div>
        </div>
        
        <div class="song-info">
            <div class="album-art">🎵</div>
            <div class="song-info-details">
                <div class="song-title-display">{os.path.basename(st.session_state.songs[st.session_state.current_song_index])}</div>
                <div>Unknown Artist</div>
            </div>
        </div>
        
        <div class="volume-control">
            <div class="volume-icon">🔊</div>
            <div class="volume-bar">
                <div class="volume-level" style="width: {st.session_state.volume}%;"></div>
                <div class="volume-knob"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Current gesture display
    if st.session_state.webcam_active:
        st.markdown('<div class="status-box">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-weight: 600; margin-bottom: 12px;">Current Gesture</div>
        <div class="gesture-value" style="text-align: center; padding: 12px 0;">{st.session_state.current_gesture}</div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Manual controls with enhanced Spotify styling
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
    
    # Gesture Guide with enhanced styling and animations
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
    
    # Quick tips section
    st.markdown('<h2 style="margin-top: 24px;">Quick Tips</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="status-box">
        <ul style="padding-left: 20px; color: #B3B3B3;">
            <li style="margin-bottom: 8px;">Hold gestures steady for 2 seconds to trigger actions</li>
            <li style="margin-bottom: 8px;">Make sure your hand is clearly visible in the camera</li>
            <li style="margin-bottom: 8px;">Good lighting improves gesture recognition</li>
            <li>Add songs to the 'songs' folder to expand your library</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Enhanced Spotify-style footer with animation
st.markdown("""
<div class="footer">
    <div class="footer-logo">💫</div>
    <p>Gesture-Controlled Media Player © 2025 • Made with ❤️</p>
</div>
""", unsafe_allow_html=True)

# Webcam processing - only runs when webcam is active
if st.session_state.webcam_active:
    # Initialize variables for gesture handling
    last_action = None
    cooldown = 2  # seconds
    last_time = time.time()
    
    # Set initial volume
    initialize_pygame()
    pygame.mixer.music.set_volume(st.session_state.volume / 100)
    
    # Start video capture
    try:
        for frame, landmarks in detect_hands_in_video(video_path=None, is_webcam=True):
            # Check if the webcam should still be active
            if not st.session_state.webcam_active:
                break
                
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
            
            # Update progress for visual feedback when playing
            if st.session_state.current_status == "playing":
                update_progress()
            
            # Convert to RGB for display
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Add gesture indicator overlay to the frame
            if action is not None:
                overlay = frame_rgb.copy()
                text_position = (20, frame_rgb.shape[0] - 30)
                cv2.putText(overlay, f"Gesture: {action}", text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Add a semi-transparent background for better text visibility
                x, y = text_position
                text_size, _ = cv2.getTextSize(f"Gesture: {action}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                cv2.rectangle(frame_rgb, (x-10, y+10), (x+text_size[0]+10, y-text_size[1]-10), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.8, frame_rgb, 0.2, 0, frame_rgb)
                cv2.putText(frame_rgb, f"Gesture: {action}", text_position, 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
            
    except Exception as e:
        st.error(f"Error with video capture: {e}")
        video_placeholder.error("Camera access error. Please check your webcam connection and permissions.")
        st.session_state.webcam_active = False