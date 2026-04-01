import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Get screen width to calculate left/right zones
# We will use the camera resolution width (usually 640)
cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
center_zone_left = int(cam_width * 0.4)
center_zone_right = int(cam_width * 0.6)

while True:
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    # Draw zones on the screen for visual help
    cv2.line(frame, (center_zone_left, 0), (center_zone_left, 480), (255, 0, 0), 2)
    cv2.line(frame, (center_zone_right, 0), (center_zone_right, 480), (255, 0, 0), 2)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get coordinates for Index Finger Tip (8) and Pip joint (6)
            index_tip = hand_landmarks.landmark[8]
            index_pip = hand_landmarks.landmark[6]
            
            # Convert normalized coordinates (0 to 1) to pixel coordinates
            x_pixel = int(index_tip.x * cam_width)
            
            gesture = "Accelerating"
            
            # 1. Check if hand is closed (Fist = Brake)
            # In computer vision, Y increases as it goes DOWN. 
            # So if tip Y is greater than joint Y, the finger is folded down.
            if index_tip.y > index_pip.y:
                gesture = "Braking"
            else:
                # 2. Steer based on X coordinate
                if x_pixel < center_zone_left:
                    gesture = "Steering LEFT"
                elif x_pixel > center_zone_right:
                    gesture = "Steering RIGHT"
                else:
                    gesture = "Accelerating STRAIGHT"
            
            # Display the gesture on the screen
            cv2.putText(frame, gesture, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Racing Game Gesture Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()