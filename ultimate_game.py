import cv2
import mediapipe as mp
import pygame
import math
import random
import sys
import os

# ==========================================
# 1. SETUP CAMERA & AI
# ==========================================
cap = cv2.VideoCapture(0) 
cam_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
cam_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
center_zone_left = int(cam_width * 0.4)
center_zone_right = int(cam_width * 0.6)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# ==========================================
# 2. SETUP PYGAME & ASSETS
# ==========================================
pygame.init()
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Gesture Racing - ULTIMATE")
clock = pygame.time.Clock()

# Colors
GRASS_GREEN = (34, 139, 34)
ROAD_GRAY = (80, 80, 80)
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
RED = (200, 50, 50)

# Game Variables
car_w, car_h = 50, 100
player_x, player_y = WIDTH // 2 - car_w // 2, HEIGHT - car_h - 50
player_speed_x, base_speed, score = 10, 5, 0

# --- ASSET LOADER (The Magic Trick) ---
# It tries to load images, but won't crash if you don't have them yet!
use_images = False
# === In ultimate_game.py, under Step 2: Setup Pygame & Assets ===

# Old (broken):
# player_img = pygame.transform.scale(pygame.image.load("player.png"), (car_w, car_h))
# enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), (car_w, car_h))
# tree_img = pygame.transform.scale(pygame.image.load("tree.png"), (80, 100))

# New (FIXED!):
try:
    player_img = pygame.transform.scale(pygame.image.load("player.png").convert_alpha(), (car_w, car_h))
    enemy_img = pygame.transform.scale(pygame.image.load("enemy.png").convert_alpha(), (car_w, car_h))
    tree_img = pygame.transform.scale(pygame.image.load("tree.png").convert_alpha(), (80, 100))
    use_images = True
except:
    print("Images not found! Using shape mode until you add player.png, enemy.png, and tree.png")

# Level Design Objects
# Traffic stays on the gray road (x between 100 and 450)
traffic = [pygame.Rect(random.choice([130, 275, 420]), -i * 300, car_w, car_h) for i in range(3)]
lines = [pygame.Rect(WIDTH//2 - 5, i * 100, 10, 50) for i in range(10)]

# Trees spawn on the grass (x < 100 or x > 500)
trees = []
for i in range(6):
    trees.append(pygame.Rect(10, i * 150, 80, 100)) # Left side trees
    trees.append(pygame.Rect(WIDTH - 90, (i * 150) + 75, 80, 100)) # Right side trees

running, game_over = True, False

# ==========================================
# 3. MAIN GAME LOOP
# ==========================================
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- AI VISION ---
    success, frame = cap.read()
    if not success: break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    steer_left = steer_right = is_braking = is_nitro = has_hand = False

    if result.multi_hand_landmarks:
        has_hand = True
        hand_landmarks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        index_tip, index_pip, thumb_tip = hand_landmarks.landmark[8], hand_landmarks.landmark[6], hand_landmarks.landmark[4]
        index_x, index_y = int(index_tip.x * cam_width), int(index_tip.y * cam_height)
        thumb_x, thumb_y = int(thumb_tip.x * cam_width), int(thumb_tip.y * cam_height)

        if math.hypot(thumb_x - index_x, thumb_y - index_y) < 40: is_nitro = True
        elif index_tip.y > index_pip.y: is_braking = True
        elif index_x < center_zone_left: steer_left = True
        elif index_x > center_zone_right: steer_right = True

    cv2.imshow("Camera Sensor", frame)
    cv2.waitKey(1)

    # --- GAME ENGINE ---
    if not game_over:
        if not has_hand: current_speed = 0 
        elif is_braking: current_speed = base_speed * 0.5
        elif is_nitro: current_speed = base_speed * 3
        else: current_speed = base_speed * 1.5

        # Move Player (Confine to the road boundaries)
        if steer_left and player_x > 100: player_x -= player_speed_x
        if steer_right and player_x < WIDTH - 100 - car_w: player_x += player_speed_x
        player_rect = pygame.Rect(player_x, player_y, car_w, car_h)

        # Move Environment (Road Lines and Trees)
        for line in lines:
            line.y += current_speed
            if line.y > HEIGHT: line.y = -50
            
        for tree in trees:
            tree.y += current_speed
            if tree.y > HEIGHT: tree.y = -100

        # Move Traffic
        for car in traffic:
            car.y += current_speed * 0.8
            if car.y > HEIGHT:
                car.y = random.randint(-400, -100)
                car.x = random.choice([130, 275, 420])
                score += 1
            if player_rect.colliderect(car):
                game_over = True

    else: 
        if has_hand and not is_braking and not is_nitro: 
            game_over, score = False, 0
            traffic = [pygame.Rect(random.choice([130, 275, 420]), -i * 300, car_w, car_h) for i in range(3)]
            player_x = WIDTH // 2 - car_w // 2

    # --- DRAWING ---
    screen.fill(GRASS_GREEN) # Draw Grass Background
    pygame.draw.rect(screen, ROAD_GRAY, (100, 0, 400, HEIGHT)) # Draw Gray Road
    pygame.draw.rect(screen, YELLOW, (95, 0, 10, HEIGHT)) # Left yellow line
    pygame.draw.rect(screen, YELLOW, (495, 0, 10, HEIGHT)) # Right yellow line

    for line in lines: pygame.draw.rect(screen, WHITE, line)

    # Draw Trees
    for tree in trees:
        if use_images: screen.blit(tree_img, (tree.x, tree.y))
        else: pygame.draw.rect(screen, (0, 100, 0), tree) # Backup tree box

    # Draw Traffic
    for car in traffic:
        if use_images: screen.blit(enemy_img, (car.x, car.y))
        else: pygame.draw.rect(screen, RED, car)

    # Draw Player & Nitro Flames!
    if not game_over and is_nitro and has_hand:
        # Draw a cool flame coming out of the back when boosting!
        pygame.draw.rect(screen, (255, 140, 0), (player_x + 15, player_y + car_h, 20, 30 + random.randint(-10, 10)))

    if use_images:
        screen.blit(player_img, (player_x, player_y))
    else:
        player_color = (50, 150, 255) if is_nitro else (50, 200, 50)
        if game_over: player_color = (50, 50, 50)
        pygame.draw.rect(screen, player_color, player_rect)

    # UI Text
    font = pygame.font.SysFont(None, 48)
    screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 20))
    if game_over: screen.blit(font.render("CRASHED! Open hand to restart", True, RED), (60, HEIGHT//2))
    elif not has_hand: screen.blit(font.render("Show hand to camera to play!", True, WHITE), (70, HEIGHT//2))

    pygame.display.flip()
    clock.tick(30)

cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()