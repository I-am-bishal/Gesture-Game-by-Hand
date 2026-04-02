import cv2
import mediapipe as mp
import pyautogui
import math # Added for distance calculation

pyautogui.PAUSE = 0 

# Use 0, 1, or 2 depending on which one worked for your laptop
cap = cv2.VideoCapture(0)
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
    
    cv2.line(frame, (center_zone_left, 0), (center_zone_left, cam_height), (255, 0, 0), 2)
    cv2.line(frame, (center_zone_right, 0), (center_zone_right, cam_height), (255, 0, 0), 2)

    gesture = "Idle"

    if result.multi_hand_landmarks:
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        # Get Landmarks
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        thumb_tip = hand_landmarks.landmark[4]
        
        # Convert to exact pixel coordinates
        index_x, index_y = int(index_tip.x * cam_width), int(index_tip.y * cam_height)
        thumb_x, thumb_y = int(thumb_tip.x * cam_width), int(thumb_tip.y * cam_height)
        
        # Calculate the distance between Thumb and Index Finger
        pinch_distance = math.hypot(thumb_x - index_x, thumb_y - index_y)
        
        # Draw a line between the thumb and index finger so you can see the connection
        cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 255), 3)
        
        # Logic 1: Check for Pinch (Nitro)
        if pinch_distance < 40: # If fingers are closer than 40 pixels
            gesture = "NITRO BOOST! (Shift)"
            press_key('shift')
            # You can still steer while boosting!
            if index_x < center_zone_left:
                press_key('a')
                release_key('d')
            elif index_x > center_zone_right:
                press_key('d')
                release_key('a')
            else:
                release_key('a')
                release_key('d')
                
        # Logic 2: Check for Fist (Brake)
        elif index_tip.y > index_pip.y:
            gesture = "Braking (S)"
            release_key('shift')
            release_key('w')
            release_key('a')
            release_key('d')
            press_key('s')
            
        # Logic 3: Normal Driving (Accelerate and Steer)
        else:
            release_key('shift')
            release_key('s')
            press_key('w') 
            
            if index_x < center_zone_left:
                gesture = "Left (W+A)"
                press_key('a')
                release_key('d')
            elif index_x > center_zone_right:
                gesture = "Right (W+D)"
                press_key('d')
                release_key('a')
            else:
                gesture = "Straight (W)"
                release_key('a')
                release_key('d')
    else:
        release_all_keys()
        
    # Make the Nitro text pop with a different color!
    text_color = (0, 165, 255) if "NITRO" in gesture else (0, 255, 0)
    cv2.putText(frame, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 3)
    
    cv2.imshow("Racing Game Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

release_all_keys()
cap.release()
cv2.destroyAllWindows()