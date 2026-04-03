import cv2
import mediapipe as mp
import pygame
import math
import random
import sys

# ==========================================
# 1. SETUP CAMERA & AI
# ==========================================
cap = cv2.VideoCapture(0) # Change to 1 or 2 if camera doesn't open
cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
center_zone_left = int(cam_width * 0.4)
center_zone_right = int(cam_width * 0.6)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# ==========================================
# 2. SETUP PYGAME
# ==========================================
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Gesture Racing - ULTIMATE")
clock = pygame.time.Clock()

# Colors & Game Variables
GRAY, WHITE, GREEN, RED, BLUE = (100, 100, 100), (255, 255, 255), (50, 200, 50), (200, 50, 50), (50, 150, 255)
car_w, car_h = 50, 100
player_x, player_y = WIDTH // 2 - car_w // 2, HEIGHT - car_h - 50
player_speed_x, base_speed, score = 10, 5, 0

traffic = [pygame.Rect(random.choice([100, 250, 400]), -i * 300, car_w, car_h) for i in range(3)]
lines = [pygame.Rect(WIDTH//2 - 5, i * 100, 10, 50) for i in range(10)]

running, game_over = True, False

# ==========================================
# 3. MAIN GAME LOOP
# ==========================================
while running:
    # Allow closing the game window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- AI VISION ---
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    # Default gesture states
    steer_left = steer_right = is_braking = is_nitro = has_hand = False

    if result.multi_hand_landmarks:
        has_hand = True
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        index_tip, index_pip, thumb_tip = hand_landmarks.landmark[8], hand_landmarks.landmark[6], hand_landmarks.landmark[4]
        index_x, index_y = int(index_tip.x * cam_width), int(index_tip.y * cam_height)
        thumb_x, thumb_y = int(thumb_tip.x * cam_width), int(thumb_tip.y * cam_height)

        # Check Gestures
        if math.hypot(thumb_x - index_x, thumb_y - index_y) < 40:
            is_nitro = True
        elif index_tip.y > index_pip.y:
            is_braking = True
        elif index_x < center_zone_left:
            steer_left = True
        elif index_x > center_zone_right:
            steer_right = True

    # Show the little camera window in the corner
    cv2.imshow("Camera Sensor", frame)
    cv2.waitKey(1)

    # --- GAME ENGINE ---
    if not game_over:
        if not has_hand:
            current_speed = 0 # PAUSE the game if no hand is visible!
        elif is_braking:
            current_speed = base_speed * 0.5
        elif is_nitro:
            current_speed = base_speed * 3
        else:
            current_speed = base_speed * 1.5

        # Move Player
        if steer_left and player_x > 50: player_x -= player_speed_x
        if steer_right and player_x < WIDTH - 50 - car_w: player_x += player_speed_x
        player_rect = pygame.Rect(player_x, player_y, car_w, car_h)

        # Move Road & Traffic
        for line in lines:
            line.y += current_speed
            if line.y > HEIGHT: line.y = -50

        for car in traffic:
            car.y += current_speed * 0.8
            if car.y > HEIGHT:
                car.y = random.randint(-300, -100)
                car.x = random.choice([100, 250, 400])
                score += 1
            if player_rect.colliderect(car):
                game_over = True

    else: # If crashed, open hand (not braking or nitro) to restart
        if has_hand and not is_braking and not is_nitro: 
            game_over, score = False, 0
            traffic = [pygame.Rect(random.choice([100, 250, 400]), -i * 300, car_w, car_h) for i in range(3)]
            player_x = WIDTH // 2 - car_w // 2

    # --- DRAWING ---
    screen.fill(GRAY)
    for line in lines: pygame.draw.rect(screen, WHITE, line)
    for car in traffic: pygame.draw.rect(screen, RED, car)

    player_color = BLUE if is_nitro else GREEN
    if game_over: player_color = (100, 100, 100)
    pygame.draw.rect(screen, player_color, player_rect)

    font = pygame.font.SysFont(None, 48)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 20))
    
    if game_over:
        screen.blit(font.render("CRASHED! Open hand to restart", True, RED), (50, HEIGHT//2))
    elif not has_hand:
        screen.blit(font.render("Show hand to camera to play!", True, WHITE), (70, HEIGHT//2))

    pygame.display.flip()
    clock.tick(30) # Run at 30 FPS to perfectly match the webcam speed

cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()