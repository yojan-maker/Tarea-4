import pygame
import random
import os
import sys

# --- Inicialización ---------
pygame.init()
SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Juego de Evasión 3")
clock = pygame.time.Clock()

# -------- Colores -----
RED    = (255, 0, 0)
GREEN  = (0, 255, 0)
BLUE   = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (200, 0, 200)
BLACK  = (0, 0, 0)
WHITE  = (255, 255, 255)
GRASS  = (30, 150, 30)
ASPHALT = (50, 50, 50)
EDGE_LINE = (255, 255, 255)
LANE_LINE = (255, 255, 255)

# -- Paths --
ASSET_PATH = "assets"

# ------- Música retro de fondo -----
pygame.mixer.init()
music_path = os.path.join(ASSET_PATH, "sounds", "retro_music2.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)  
    pygame.mixer.music.play(-1)         # loop infinito

# --- Función para cargar imágenes --
def load_image(name, size):
    try:
        image = pygame.image.load(os.path.join(ASSET_PATH, name))
        return pygame.transform.scale(image, size)
    except:
        surface = pygame.Surface(size, pygame.SRCALPHA)
        color = RED if "player" in name else BLUE
        pygame.draw.rect(surface, color, (10, 15, size[0]-20, size[1]-30), border_radius=10)
        pygame.draw.rect(surface, (150, 220, 255), (15, 20, size[0]-30, 20), border_radius=5)
        pygame.draw.rect(surface, (150, 220, 255), (15, size[1]-50, size[0]-30, 20), border_radius=5)
        pygame.draw.circle(surface, BLACK, (20, size[1]-15), 12)
        pygame.draw.circle(surface, BLACK, (size[0]-20, size[1]-15), 12)
        pygame.draw.circle(surface, (100, 100, 100), (20, size[1]-15), 8)
        pygame.draw.circle(surface, (100, 100, 100), (size[0]-20, size[1]-15), 8)
        pygame.draw.circle(surface, YELLOW, (15, 25), 5)
        pygame.draw.circle(surface, YELLOW, (size[0]-15, 25), 5)
        return surface

# ---------- Jugador ----
player_w, player_h = 115, 100
player_img = load_image("car_player.png", (player_w, player_h))
player_y = SCREEN_H - player_h - 20
LANES = 4
ROAD_WIDTH = 480
ROAD_LEFT = (SCREEN_W - ROAD_WIDTH) // 2
LANE_W = ROAD_WIDTH // LANES
LANE_CENTERS = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(LANES)]

def player_rect(player_lane):
    x = LANE_CENTERS[player_lane] - player_w // 2
    return pygame.Rect(x, player_y, player_w, player_h)

def draw_player(player_lane):
    screen.blit(player_img, player_rect(player_lane))

# ------ Enemigos ----------
enemy_w, enemy_h = 115, 100
enemy_imgs = [
    load_image(f"car_enemy{i}.png", (enemy_w, enemy_h)) for i in range(1, 7)
]

def spawn_enemy(level=1):
    lane = random.randrange(LANES)
    x = LANE_CENTERS[lane] - enemy_w // 2
    img = random.choice(enemy_imgs)
    speed_modifier = 0
    if level == 2:
        speed_modifier = random.uniform(0.5, 1.5)
    elif level == 3:
        speed_modifier = random.uniform(1.0, 2.0)
    return [x, -enemy_h, img, lane, speed_modifier]

def draw_enemy(enemy):
    screen.blit(enemy[2], (enemy[0], enemy[1]))

# --------------- Partículas ----
particles = []

def add_particles(x, y, color, count=10):
    for _ in range(count):
        particles.append({
            'x': x,'y': y,'color': color,
            'size': random.randint(3, 8),
            'vx': random.uniform(-2, 2),
            'vy': random.uniform(-3, -1),
            'life': random.randint(20, 40)
        })

def update_particles():
    global particles
    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 1
        if p['life'] <= 0: particles.remove(p)

def draw_particles():
    for p in particles:
        alpha = min(255, p['life'] * 6)
        color = p['color'] + (alpha,)
        pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), p['size'])

# ---- Dibujo carretera ------------------
def draw_road(dash_offset, level=1):
    screen.fill(GRASS)
    asphalt_color = ASPHALT
    if level == 2: asphalt_color = (45,45,45)
    elif level == 3: asphalt_color = (35,35,35)
    pygame.draw.rect(screen, asphalt_color, (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_H))
    pygame.draw.line(screen, EDGE_LINE, (ROAD_LEFT+4,0),(ROAD_LEFT+4,SCREEN_H),6)
    pygame.draw.line(screen, EDGE_LINE, (ROAD_LEFT+ROAD_WIDTH-4,0),(ROAD_LEFT+ROAD_WIDTH-4,SCREEN_H),6)
    dash_h, gap = 40, 40
    speed_factor = 1.0 if level==1 else (1.3 if level==2 else 1.7)
    for i in range(1, LANES):
        x = ROAD_LEFT + i*LANE_W
        y = -dash_h + ((dash_offset * speed_factor) % (dash_h + gap))
        while y < SCREEN_H:
            pygame.draw.rect(screen, LANE_LINE, (x-3,y,6,dash_h))
            y += dash_h + gap

# ---- Fuente ---------
try:
    font = pygame.font.Font(os.path.join(ASSET_PATH,"fonts/PressStart2P.ttf"), 20)
    small_font = pygame.font.Font(os.path.join(ASSET_PATH,"fonts/PressStart2P.ttf"), 16)
except:
    font = pygame.font.SysFont("consolas", 20)
    small_font = pygame.font.SysFont("consolas",16)

def draw_text_shadow(text, x, y, color=GREEN, shadow_color=BLACK, font_type=font):
    shadow = font_type.render(text, True, shadow_color)
    screen.blit(shadow, (x+2, y+2))
    main = font_type.render(text, True, color)
    screen.blit(main, (x, y))

# ---- Bucle principal de juego -
def game_loop(base_speed, spawn_rate, max_enemies, level, lives):
    global particles
    player_lane = LANES//2
    particles = []
    enemies, score = [], 0
    running, dash_offset, invulnerable = True, 0, 0
    level_complete_score = 1000 * level

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a): player_lane = max(0, player_lane-1)
                if event.key in (pygame.K_RIGHT, pygame.K_d): player_lane = min(LANES-1, player_lane+1)
        dash_offset += base_speed
        if invulnerable>0: invulnerable-=1
        update_particles()

        if random.randint(1,spawn_rate)==1 and len(enemies)<max_enemies:
            new_enemy = spawn_enemy(level)
            too_close = any(abs(e[1]-new_enemy[1])<enemy_h*1.2 and e[3]==new_enemy[3] for e in enemies)
            if not too_close: enemies.append(new_enemy)

        for e in enemies[:]:
            individual_speed = base_speed + e[4]
            e[1] += individual_speed
            if e[1] > SCREEN_H:
                enemies.remove(e)
                score += 10

        p_rect = player_rect(player_lane)
        for e in enemies:
            enemy_rect = pygame.Rect(e[0], e[1], enemy_w, enemy_h)
            if p_rect.colliderect(enemy_rect) and invulnerable<=0:
                add_particles(p_rect.centerx, p_rect.centery, (255,50,50), 20)
                lives -= 1
                invulnerable = 60
                if lives <=0: running=False
                break
        if score >= level_complete_score:
            show_level_complete(level, score)
            return True

        draw_road(dash_offset, level)
        for e in enemies: draw_enemy(e)
        if invulnerable<=0 or invulnerable%6<3: draw_player(player_lane)
        draw_particles()

        score += 0.1
        score_color = GREEN if level==1 else (ORANGE if level==2 else RED)
        draw_text_shadow(f"Puntuación: {int(score)}", 10, 10, score_color)
        draw_text_shadow(f"Nivel: {level}", 10, 40)
        lives_color = GREEN if lives>=3 else (ORANGE if lives==2 else RED)
        draw_text_shadow(f"Vidas: {lives}", 10, 70, lives_color)
        draw_text_shadow(f"Objetivo: {level_complete_score}", SCREEN_W-350, 10)
        draw_text_shadow(f"Velocidad: {'■'*level}", SCREEN_W-250, 40, score_color)

        pygame.display.update()
        clock.tick(60)

    show_game_over(int(score), level)
    return False

# --- Pantallas de fin de nivel y game over ----
def show_level_complete(level, score):
    screen.fill(BLACK)
    draw_text_shadow(f"¡Nivel {level} completado!", SCREEN_W//2-250, SCREEN_H//2-50, GREEN)
    draw_text_shadow(f"Puntuación: {int(score)}", SCREEN_W//2-180, SCREEN_H//2+20, WHITE)
    if level<3:
        draw_text_shadow("Presiona cualquier tecla", SCREEN_W//2-300, SCREEN_H//2+90, YELLOW, font_type=small_font)
        draw_text_shadow("para continuar", SCREEN_W//2-200, SCREEN_H//2+130, YELLOW, font_type=small_font)
    else:
        draw_text_shadow("¡FELICIDADES!", SCREEN_W//2-180, SCREEN_H//2+90, PURPLE)
        draw_text_shadow("¡Completaste todos los niveles!", SCREEN_W//2-320, SCREEN_H//2+130, PURPLE, font_type=small_font)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN: return

def show_game_over(score, level):
    screen.fill(BLACK)
    draw_text_shadow("¡GAME OVER!", SCREEN_W//2-180, SCREEN_H//2-50, RED)
    draw_text_shadow(f"Puntuación final: {score}", SCREEN_W//2-240, SCREEN_H//2+20, WHITE)
    draw_text_shadow(f"Nivel alcanzado: {level}", SCREEN_W//2-240, SCREEN_H//2+60, ORANGE)
    draw_text_shadow("Presiona cualquier tecla", SCREEN_W//2-300, SCREEN_H//2+120, YELLOW, font_type=small_font)
    draw_text_shadow("para volver al menú", SCREEN_W//2-240, SCREEN_H//2+160, YELLOW, font_type=small_font)
    pygame.display.update()
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN: return

# --- Menú principal ---
def menu():
    option = 0
    options = ["Fácil", "Medio", "Difícil"]
    descriptions = [
        "Velocidad moderada, pocos enemigos",
        "Velocidad alta, más enemigos",
        "Velocidad EXTREMA, muchos enemigos"
    ]
    colors = [GREEN, ORANGE, RED]

    # --- Música de fondo desde el menú -<---
    if os.path.exists(music_path):
        pygame.mixer.music.play(-1)

    # --- Fondo menú ---
    try:
        menu_bg = pygame.image.load(os.path.join(ASSET_PATH,"menu_bg.png"))
        menu_bg = pygame.transform.scale(menu_bg, (SCREEN_W, SCREEN_H))
    except:
        menu_bg = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(0, SCREEN_H, 4):
            pygame.draw.line(menu_bg, (30,30,100), (0,y),(SCREEN_W,y))

    while True:
        screen.blit(menu_bg, (0,0))
        draw_text_shadow("JUEGO DE EVASIÓN 3", SCREEN_W//2-250, 60, (255,200,0))
        draw_text_shadow("Selecciona dificultad:", SCREEN_W//2-240, 120)
        for i, text in enumerate(options):
            color = colors[i] if i==option else WHITE
            y_pos = 200 + i*80
            draw_text_shadow(f"{text}", SCREEN_W//2-100, y_pos, color)
            draw_text_shadow(descriptions[i], SCREEN_W//2-380, y_pos+40, colors[i], font_type=small_font)
        draw_text_shadow("Controles:", SCREEN_W//2-100, 500)
        draw_text_shadow("← → para moverse entre carriles", SCREEN_W//2-350, 540, WHITE, (50,50,50), small_font)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type==pygame.QUIT: pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP: option = (option-1)%len(options)
                if event.key==pygame.K_DOWN: option = (option+1)%len(options)
                if event.key==pygame.K_RETURN:
                    if option==0: game_loop(5,25,2,1,3)
                    elif option==1: game_loop(7,18,3,2,3)
                    elif option==2: game_loop(9,12,5,3,2)

if __name__ == "__main__":
    menu()

