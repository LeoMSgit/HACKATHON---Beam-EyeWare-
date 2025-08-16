import sys
import time
import random
import pygame
from eyeware.beam_eye_tracker import API, ViewportGeometry, Point, TrackingConfidence, NULL_DATA_TIMESTAMP

# ---------------------------
# Configuração do Tracker
# ---------------------------
def initialize_tracker(screen_width, screen_height):
    """Configura e inicializa o rastreador ocular com a resolução correta"""
    try:
        viewport = ViewportGeometry()
        viewport.point_00 = Point(0, 0)
        viewport.point_11 = Point(screen_width, screen_height)
        
        tracker_api = API("ProGamerEyeTrainer", viewport)
        
        if tracker_api.attempt_starting_the_beam_eye_tracker():
            print("Rastreador ocular iniciado com sucesso")
            return tracker_api
        else:
            print("Falha ao iniciar o rastreador ocular")
            return None
    except Exception as e:
        print(f"Erro ao inicializar o rastreador: {str(e)}")
        return None

# ---------------------------
# Configuração do Pygame
# ---------------------------
# Obter informações sobre o monitor antes de inicializar o Pygame
pygame.init()
info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
print(f"Resolução detectada: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Configurar a tela em modo fullscreen com a resolução correta
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Pro Gamer Eye Trainer")

# Carregar fontes
try:
    font = pygame.font.SysFont("Arial", 36)
    small_font = pygame.font.SysFont("Arial", 24)
except:
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

# Cores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (100, 150, 255)
BLACK = (0, 0, 0)
BACKGROUND = (20, 20, 30)

# ---------------------------
# Funções auxiliares
# ---------------------------
def gaze_to_screen(gaze_point, offset_x=0, offset_y=0):
    """Converte coordenadas de gaze para coordenadas de tela"""
    try:
        # Normaliza as coordenadas para a resolução real da tela
        norm_x = gaze_point.x / SCREEN_WIDTH
        norm_y = gaze_point.y / SCREEN_HEIGHT
        
        # Converte para coordenadas de tela
        gx = int(norm_x * SCREEN_WIDTH + offset_x)
        gy = int(norm_y * SCREEN_HEIGHT + offset_y)
        
        # Limita aos limites da tela
        gx = max(0, min(SCREEN_WIDTH, gx))
        gy = max(0, min(SCREEN_HEIGHT, gy))
        
        return gx, gy
    except:
        return SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

def get_valid_gaze(tracker_api):
    """Obtém a posição válida do olhar"""
    if not tracker_api:
        return None
        
    try:
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
    except:
        return None

# ---------------------------
# Calibração
# ---------------------------
def perform_calibration(tracker_api):
    """Realiza a calibração do rastreador ocular"""
    calibration_points = [
        (50, 50),
        (SCREEN_WIDTH - 50, 50),
        (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50),
        (50, SCREEN_HEIGHT - 50),
        (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Ponto central
    ]
    
    offset_x_total = 0
    offset_y_total = 0
    samples = 15  # amostras por ponto
    valid_samples = 0
    
    for px, py in calibration_points:
        for i in range(samples):
            screen.fill(BACKGROUND)
            
            # Desenha ponto de calibração
            pygame.draw.circle(screen, RED, (px, py), 25)
            pygame.draw.circle(screen, (180, 0, 0), (px, py), 30, 3)
            
            # Mostra progresso
            point_index = calibration_points.index((px, py)) + 1
            progress = font.render(f"Calibrando... Ponto {point_index}/5", True, WHITE)
            screen.blit(progress, (SCREEN_WIDTH // 2 - progress.get_width() // 2, 30))
            
            pygame.display.flip()
            
            # Obtém dados do olhar
            gaze = get_valid_gaze(tracker_api)
            if gaze:
                gx, gy = gaze_to_screen(gaze.point_of_regard)
                offset_x_total += (px - gx)
                offset_y_total += (py - gy)
                valid_samples += 1
            
            time.sleep(0.05)
    
    if valid_samples > 0:
        offset_x = offset_x_total / valid_samples
        offset_y = offset_y_total / valid_samples
        print(f"Calibração concluída. Offset: X={offset_x:.2f}, Y={offset_y:.2f}")
        return offset_x, offset_y
    else:
        print("Calibração falhou - usando offset zero")
        return 0, 0

# ---------------------------
# Configuração do jogo
# ---------------------------
# Inicializar tracker
tracker_api = initialize_tracker(SCREEN_WIDTH, SCREEN_HEIGHT)

# Realizar calibração
offset_x, offset_y = perform_calibration(tracker_api)

# Configurações do jogo
target_radius = 30
reaction_times = []
target_pos = (random.randint(target_radius, SCREEN_WIDTH - target_radius),
              random.randint(target_radius, SCREEN_HEIGHT - target_radius))
target_visible = True
target_appeared_at = time.time()

# Variáveis para a mira verde
gaze_history = []
MAX_HISTORY = 10

# ---------------------------
# Loop principal
# ---------------------------
running = True
clock = pygame.time.Clock()

while running:
    # Preencher toda a tela para evitar bordas pretas
    screen.fill(BACKGROUND)
    
    # Desenhar grade de fundo sutil
    for x in range(0, SCREEN_WIDTH, 50):
        pygame.draw.line(screen, (30, 30, 40), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, 50):
        pygame.draw.line(screen, (30, 30, 40), (0, y), (SCREEN_WIDTH, y), 1)

    # Mostrar o alvo
    if target_visible:
        # Alvo principal
        pygame.draw.circle(screen, RED, target_pos, target_radius)
        # Contorno do alvo
        pygame.draw.circle(screen, (180, 0, 0), target_pos, target_radius + 5, 3)
        # Centro do alvo
        pygame.draw.circle(screen, (255, 200, 0), target_pos, target_radius // 3)
        
        # Temporizador visual (círculo que diminui)
        time_elapsed = time.time() - target_appeared_at
        if time_elapsed > 2.0:
            shrink = max(5, target_radius * (1 - (time_elapsed - 2.0) / 1.0))
            pygame.draw.circle(screen, (255, 150, 0), target_pos, int(shrink))

    # Eventos do Pygame
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                target_visible = True
                target_appeared_at = time.time()
            elif event.key == pygame.K_r:  # Recalibrar com R
                offset_x, offset_y = perform_calibration(tracker_api)
                gaze_history = []  # Limpar histórico

    # Obter posição do olhar
    gaze = get_valid_gaze(tracker_api)
    if gaze:
        gaze_x, gaze_y = gaze_to_screen(gaze.point_of_regard, offset_x, offset_y)
        
        # Adicionar ao histórico para suavização
        gaze_history.append((gaze_x, gaze_y))
        if len(gaze_history) > MAX_HISTORY:
            gaze_history.pop(0)
        
        # Calcular posição suavizada (média do histórico)
        if gaze_history:
            avg_x = sum(pos[0] for pos in gaze_history) / len(gaze_history)
            avg_y = sum(pos[1] for pos in gaze_history) / len(gaze_history)
            gaze_x, gaze_y = int(avg_x), int(avg_y)
        
        # Desenhar a mira verde (grande e visível)
        # Círculo interno
        pygame.draw.circle(screen, GREEN, (gaze_x, gaze_y), 12)
        # Contorno
        pygame.draw.circle(screen, (0, 180, 0), (gaze_x, gaze_y), 15, 2)
        # Cruz de precisão
        pygame.draw.line(screen, (0, 150, 0), (gaze_x - 20, gaze_y), (gaze_x + 20, gaze_y), 2)
        pygame.draw.line(screen, (0, 150, 0), (gaze_x, gaze_y - 20), (gaze_x, gaze_y + 20), 2)
        
        # Desenhar histórico da mira (rastro)
        for i, pos in enumerate(gaze_history):
            alpha = 200 - (i * 15)
            size = max(3, 5 - (i * 0.3))
            pygame.draw.circle(screen, (0, 255, 0, alpha), pos, int(size))

        # Checar se o olhar acertou o alvo
        if target_visible:
            dx = gaze_x - target_pos[0]
            dy = gaze_y - target_pos[1]
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance <= target_radius:
                reaction_time = time.time() - target_appeared_at
                reaction_times.append(reaction_time)
                target_pos = (random.randint(target_radius, SCREEN_WIDTH - target_radius),
                              random.randint(target_radius, SCREEN_HEIGHT - target_radius))
                target_appeared_at = time.time()
                target_visible = True

    # Verificar tempo limite do alvo (3 segundos)
    if target_visible and (time.time() - target_appeared_at > 3.0):
        target_visible = False
        target_appeared_at = time.time()

    # Mostrar métricas de desempenho
    if reaction_times:
        avg_reaction = sum(reaction_times) / len(reaction_times)
        min_reaction = min(reaction_times)
        
        # Fundo semitransparente para métricas
        metrics_bg = pygame.Surface((300, 110), pygame.SRCALPHA)
        metrics_bg.fill((0, 0, 0, 180))
        screen.blit(metrics_bg, (20, 20))
        
        # Textos das métricas
        avg_text = font.render(f"Tempo Médio: {avg_reaction:.3f}s", True, WHITE)
        min_text = font.render(f"Melhor Tempo: {min_reaction:.3f}s", True, WHITE)
        hits_text = font.render(f"Acertos: {len(reaction_times)}", True, WHITE)
        
        screen.blit(avg_text, (30, 30))
        screen.blit(min_text, (30, 70))
        screen.blit(hits_text, (30, 110))

    # Mostrar instruções
    instructions_bg = pygame.Surface((250, 120), pygame.SRCALPHA)
    instructions_bg.fill((0, 0, 0, 180))
    screen.blit(instructions_bg, (SCREEN_WIDTH - 270, 20))
    
    instructions = [
        "ESPAÇO: Mostrar alvo",
        "R: Recalibrar",
        "ESC: Sair"
    ]
    
    for i, text in enumerate(instructions):
        instr = small_font.render(text, True, (200, 200, 255))
        screen.blit(instr, (SCREEN_WIDTH - 260, 30 + i * 35))
    
    # Mostrar status do tracker
    status = "Rastreador: ATIVO" if tracker_api else "Rastreador: INATIVO"
    status_color = GREEN if tracker_api else RED
    status_text = small_font.render(status, True, status_color)
    screen.blit(status_text, (SCREEN_WIDTH - status_text.get_width() - 20, SCREEN_HEIGHT - 40))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
