import cv2
import mediapipe as mp
import pyautogui
import math

pyautogui.PAUSE = 0 

cap = cv2.VideoCapture(0) # Change to 1 or 2 if needed
cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
center_zone_left = int(cam_width * 0.4)
center_zone_right = int(cam_width * 0.6)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

current_keys = set()

def press_key(key):
    if key not in current_keys:
        pyautogui.keyDown(key)
        current_keys.add(key)

def release_key(key):
    if key in current_keys:
        pyautogui.keyUp(key)
        current_keys.remove(key)

def release_all_keys():
    for key in list(current_keys):
        release_key(key)

while True:
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    # Draw faint boundary lines
    cv2.line(frame, (center_zone_left, 0), (center_zone_left, cam_height), (255, 255, 255), 1)
    cv2.line(frame, (center_zone_right, 0), (center_zone_right, cam_height), (255, 255, 255), 1)

    gesture = "Idle"
    wheel_color = (255, 255, 255) # Default wheel color is White

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        # Only draw the landmarks if you want to see the AI skeleton
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        thumb_tip = hand_landmarks.landmark[4]
        
        index_x, index_y = int(index_tip.x * cam_width), int(index_tip.y * cam_height)
        thumb_x, thumb_y = int(thumb_tip.x * cam_width), int(thumb_tip.y * cam_height)
        
        pinch_distance = math.hypot(thumb_x - index_x, thumb_y - index_y)
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 255), 3)
        
        # 1. Nitro Logic
        if pinch_distance < 40:
            gesture = "NITRO BOOST! (Shift)"
            wheel_color = (0, 165, 255) # Orange in BGR
            press_key('shift')
            if index_x < center_zone_left:
                press_key('a')
                release_key('d')
            elif index_x > center_zone_right:
                press_key('d')
                release_key('a')
            else:
                release_key('a')
                release_key('d')
                
        # 2. Brake Logic
        elif index_tip.y > index_pip.y:
            gesture = "Braking (S)"
            wheel_color = (0, 0, 255) # Red in BGR
            release_key('shift')
            release_key('w')
            release_key('a')
            release_key('d')
            press_key('s')
            
        # 3. Drive/Steer Logic
        else:
            release_key('shift')
            release_key('s')
            press_key('w') 
            
            if index_x < center_zone_left:
                gesture = "Steering Left (A)"
                wheel_color = (0, 255, 0) # Green in BGR
                press_key('a')
                release_key('d')
            elif index_x > center_zone_right:
                gesture = "Steering Right (D)"
                wheel_color = (0, 255, 0) # Green in BGR
                press_key('d')
                release_key('a')
            else:
                gesture = "Accelerating (W)"
                wheel_color = (255, 255, 255) # White in BGR
                release_key('a')
                release_key('d')
    else:
        release_all_keys()
        
    # ==========================================
    # 🎨 NEW HUD (Heads-Up Display) SECTION 🎨
    # ==========================================
    
    # 1. Draw a dark background bar at the top for the text
    # cv2.rectangle(image, top_left_corner, bottom_right_corner, color, thickness (-1 means filled))
    cv2.rectangle(frame, (0, 0), (cam_width, 80), (0, 0, 0), -1)
    
    # 2. Draw the text inside the black bar
    text_color = wheel_color # Match text color to the wheel
    cv2.putText(frame, f"STATUS: {gesture}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 3)
    
    # 3. Draw the Virtual Steering Wheel at the bottom center
    wheel_center_x = cam_width // 2
    wheel_center_y = int(cam_height * 0.8) # Place it near the bottom
    
    # Outer steering wheel ring
    cv2.circle(frame, (wheel_center_x, wheel_center_y), 80, wheel_color, 8)
    # Inner steering wheel hub
    cv2.circle(frame, (wheel_center_x, wheel_center_y), 15, wheel_color, -1)
    
    # ==========================================

    cv2.imshow("Racing Game Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

release_all_keys()
cap.release()
cv2.destroyAllWindows()