import cv2
import time
import os
import pygame
import pyautogui
import pygetwindow as gw
from media_controls import map_gesture_to_action, detect_hands_in_video

# --------- Song Player Setup (using pygame) ---------
pygame.init()
pygame.mixer.init()

# Load your songs (put .mp3 or .wav files in a 'songs' folder)
song_folder = "songs"
songs = [os.path.join(song_folder, f) for f in os.listdir(song_folder) if f.endswith(('.mp3', '.wav'))]
current_song_index = 0

def play_song(index):
    pygame.mixer.music.load(songs[index])
    pygame.mixer.music.play()
    print(f"🎵 Playing: {os.path.basename(songs[index])}")

def pause_song():
    pygame.mixer.music.pause()
    print("⏸️ Paused")

def unpause_song():
    pygame.mixer.music.unpause()
    print("▶️ Resumed")

def stop_song():
    pygame.mixer.music.stop()
    print("🛑 Stopped")

def next_song():
    global current_song_index
    current_song_index = (current_song_index + 1) % len(songs)
    play_song(current_song_index)

def previous_song():
    global current_song_index
    current_song_index = (current_song_index - 1) % len(songs)
    play_song(current_song_index)

# --------- Webcam + Gesture Control Loop ---------
last_action = None
cooldown = 2  # seconds
last_time = time.time()

for frame, landmarks in detect_hands_in_video(video_path=None, is_webcam=True):
    action = map_gesture_to_action(landmarks)

    # Only act if cooldown passed
    if action != last_action and action is not None and (time.time() - last_time > cooldown):
        last_time = time.time()
        last_action = action

        # Control the music based on the detected gesture
        if action == "play":
            if pygame.mixer.music.get_busy():
                unpause_song()
            else:
                play_song(current_song_index)
        elif action == "pause":
            pause_song()
        elif action == "stop":
            stop_song()
        elif action == "next":
            next_song()
        elif action == "previous":
            previous_song()

    # Show the webcam output
    cv2.imshow("Media Control (Press Q to quit)", frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
stop_song()
