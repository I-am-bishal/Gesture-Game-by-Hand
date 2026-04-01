import cv2
import mediapipe as mp
import pyautogui

# Disable pyautogui delay to make controls snappy
pyautogui.PAUSE = 0 

cap = cv2.VideoCapture(0)
cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
center_zone_left = int(cam_width * 0.4)
center_zone_right = int(cam_width * 0.6)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Keep track of currently pressed keys so we don't spam the OS
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
    
    cv2.line(frame, (center_zone_left, 0), (center_zone_left, 480), (255, 0, 0), 2)
    cv2.line(frame, (center_zone_right, 0), (center_zone_right, 480), (255, 0, 0), 2)

    gesture = "Idle"

    if result.multi_hand_landmarks:
        # Only process the first hand detected to avoid confusion
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        x_pixel = int(index_tip.x * cam_width)
        
        if index_tip.y > index_pip.y:
            gesture = "Braking (S)"
            release_key('w')
            release_key('a')
            release_key('d')
            press_key('s')
        else:
            release_key('s')
            press_key('w') # Always gas when hand is open
            
            if x_pixel < center_zone_left:
                gesture = "Left (W+A)"
                press_key('a')
                release_key('d')
            elif x_pixel > center_zone_right:
                gesture = "Right (W+D)"
                press_key('d')
                release_key('a')
            else:
                gesture = "Straight (W)"
                release_key('a')
                release_key('d')
    else:
        # If no hand is detected, release everything
        release_all_keys()
        
    cv2.putText(frame, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Racing Game Gesture Controller", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

release_all_keys() # Clean up keys on exit
cap.release()
cv2.destroyAllWindows()