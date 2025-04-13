# media_controls.py

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
    
    # Check hand direction (thumb position relative to index finger base)
    is_right_hand = landmarks[4][0] > landmarks[0][0]
    
    # Thumb detection (different for left vs right hand)
    if is_right_hand:
        # Right hand - thumb is up if thumb tip is to the right of thumb IP joint
        fingers.append(1 if landmarks[4][0] > landmarks[3][0] else 0)
    else:
        # Left hand - thumb is up if thumb tip is to the left of thumb IP joint
        fingers.append(1 if landmarks[4][0] < landmarks[3][0] else 0)
    
    # For the other 4 fingers:
    # Each finger is considered "up" if its tip y-coordinate is lower (higher in image)
    # than the corresponding PIP joint (second knuckle)
    for finger_id in range(1, 5):
        tip_id = finger_id * 4 + 4  # Index of the fingertip landmark
        pip_id = finger_id * 4 + 2  # Index of the PIP joint landmark
        
        # Finger is extended if tip is higher than PIP joint
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
    # We check if palm is facing down (wrist landmark is higher than middle finger MCP)
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