import cv2

# 0 is usually the default built-in webcam
cap = cv2.VideoCapture(0)

while True:
    success, frame = cap.read()
    if not success:
        break
    
    # Flip the frame horizontally for a selfie-view display
    frame = cv2.flip(frame, 1)
    
    cv2.imshow("Racing Game Gesture Controller", frame)
    
    # Press 'q' to quit the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()