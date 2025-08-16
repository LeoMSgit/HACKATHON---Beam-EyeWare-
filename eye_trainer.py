import sys
import time
import random
import pygame
from eyeware.beam_eye_tracker import API, ViewportGeometry, Point, TrackingConfidence, NULL_DATA_TIMESTAMP

# ---------------------------
# Configuração do Tracker
# ---------------------------
viewport = ViewportGeometry()
viewport.point_00 = Point()
viewport.point_00.x = 0
viewport.point_00.y = 0
viewport.point_11 = Point()
viewport.point_11.x = 1920
viewport.point_11.y = 1080

tracker_api = API("ProGamerEyeTrainer", viewport)
tracker_api.attempt_starting_the_beam_eye_tracker()

# ---------------------------
# Configuração do Pygame
# ---------------------------
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()
font = pygame.font.SysFont(None, 36)

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# ---------------------------
# Funções auxiliares
# ---------------------------
def gaze_to_screen(x, y, offset_x=0, offset_y=0):
    gx = int(x / viewport.point_11.x * screen_width + offset_x)
    gy = int(y / viewport.point_11.y * screen_height + offset_y)

    # Mantém o gaze sempre visível na tela
    gx = max(0, min(screen_width - 1, gx))
    gy = max(0, min(screen_height - 1, gy))
    return gx, gy

def get_valid_gaze():
    tracking_state_set = tracker_api.get_latest_tracking_state_set()
    if tracking_state_set is None:
        return None
    user_state = tracking_state_set.user_state()
    if user_state.timestamp_in_seconds == NULL_DATA_TIMESTAMP():
        return None
    gaze = user_state.unified_screen_gaze
    if gaze.confidence == TrackingConfidence.LOST_TRACKING:
        return None
    return gaze

# ---------------------------
# Calibração rápida
# ---------------------------
calibration_points = [
    (50, 50),
    (screen_width - 50, 50),
    (screen_width - 50, screen_height - 50),
    (50, screen_height - 50)
]

offset_x_total = 0
offset_y_total = 0
samples = 20  # amostras por ponto

for px, py in calibration_points:
    for i in range(samples):
        screen.fill(BLACK)
        pygame.draw.circle(screen, RED, (px, py), 15)
        pygame.display.flip()
        gaze = get_valid_gaze()
        if gaze:
            gx, gy = gaze_to_screen(gaze.point_of_regard.x, gaze.point_of_regard.y)
            offset_x_total += (px - gx)
            offset_y_total += (py - gy)
        time.sleep(0.05)

# Média dos offsets
offset_x = offset_x_total / (samples * len(calibration_points))
offset_y = offset_y_total / (samples * len(calibration_points))

# ---------------------------
# Configuração do jogo
# ---------------------------
target_radius = 30
reaction_times = []

def new_target():
    """Gera novo alvo sempre dentro da tela"""
    return (
        random.randint(target_radius, screen_width - target_radius),
        random.randint(target_radius, screen_height - target_radius)
    )

target_pos = new_target()
target_visible = True
target_appeared_at = time.time()

# ---------------------------
# Loop principal
# ---------------------------
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(BLACK)

    # Mostra o alvo
    if target_visible:
        pygame.draw.circle(screen, RED, target_pos, target_radius)

    # Eventos do Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # Polling do gaze
    gaze = get_valid_gaze()
    if gaze:
        gaze_x, gaze_y = gaze_to_screen(gaze.point_of_regard.x, gaze.point_of_regard.y, offset_x, offset_y)
        pygame.draw.circle(screen, GREEN, (gaze_x, gaze_y), 5)

        # Checa se o gaze acertou o alvo
        if target_visible:
            dx = gaze_x - target_pos[0]
            dy = gaze_y - target_pos[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= target_radius:
                reaction_time = time.time() - target_appeared_at
                reaction_times.append(reaction_time)
                target_pos = new_target()
                target_appeared_at = time.time()

    # Mostra métricas
    if reaction_times:
        avg_reaction = sum(reaction_times) / len(reaction_times)
        text = font.render(f"Avg Reaction: {avg_reaction:.3f}s  Hits: {len(reaction_times)}", True, WHITE)
        screen.blit(text, (20, 20))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
