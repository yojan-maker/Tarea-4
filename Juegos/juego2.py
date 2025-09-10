import pygame
import random
import sys
import os
import math

# --Inicialización
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Agar.io Style - Juego de Recolección")
clock = pygame.time.Clock()

# --Colores
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PINK = (255, 105, 180)

# --Jugador
player_radius = 20
player_x = 400
player_y = 300
player_speed = 3
invincible = False
invincible_timer = 0

# --Comida
food = []
food_radius = 5
food_colors = [GREEN, YELLOW, PURPLE, ORANGE, CYAN]

# ---Bombas--
bombs = []
bomb_radius = 10

# ---Láseres--
lasers = []
laser_width = 6
laser_spawn_timer = 0

# --Enemigos
enemies = []
enemy_min_radius = 15
enemy_max_radius = 40
enemy_speed_min = 1
enemy_speed_max = 2.5

# --Variables del juego
score = 0
level = 1
max_level = 3
score_to_next_level = 100
game_over = False
game_won = False

# --Fuentes
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# --- Cargar imagenes --
ASSET_PATH = "assets"

def load_image(name):
    if not os.path.exists(ASSET_PATH):
        os.makedirs(ASSET_PATH)
    try:
        return pygame.image.load(os.path.join(ASSET_PATH, name)).convert_alpha()
    except:
        img = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.circle(img, RED, (50, 50), 50)
        pygame.draw.circle(img, BLACK, (50, 50), 50, 2)
        return img

player_img = load_image("player_agar.png")
enemy_imgs = [
    load_image("enemy_agar1.png"),
    load_image("enemy_agar2.png"),
    load_image("enemy_agar3.png"),
    load_image("enemy_agar4.png"),
]

# --- Funciones auxiliares -
def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_circle(surface, color, center, radius):
    pygame.draw.circle(surface, color, center, radius)
    pygame.draw.circle(surface, BLACK, center, radius, 2)

def draw_image_circle(img, x, y, radius):
    size = int(radius * 2)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius)

    original_width, original_height = img.get_size()
    scale = min(size / original_width, size / original_height)
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    scaled_img = pygame.transform.smoothscale(img, (new_width, new_height))
    final_img = pygame.Surface((size, size), pygame.SRCALPHA)
    final_img.blit(scaled_img, ((size - new_width) // 2, (size - new_height) // 2))

    final_img.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    screen.blit(final_img, (int(x - radius), int(y - radius)))

def start_new_level():
    global level, enemies, bombs, lasers, score_to_next_level, player_radius, player_speed
    level += 1
    enemies = []
    bombs = []
    lasers = []
    
    if level == 2:
        # Para hacerlo mas rapido que el nivel 1
        player_radius = max(15, player_radius - 2)
        player_speed = 3.3
    elif level == 3:
        # Para hacerlo mas dificil
        player_radius = max(12, player_radius - 3)
        player_speed = 3.8
    
    for _ in range(5 + level * 2):
        spawn_enemy()
    
    score_to_next_level = score + 150 * level

def spawn_enemy():
    radius = random.randint(enemy_min_radius + level*2, enemy_max_radius + level*3)
    x = random.randint(radius, 800 - radius)
    y = random.randint(radius, 600 - radius)
    
    while math.hypot(x - player_x, y - player_y) < 150:
        x = random.randint(radius, 800 - radius)
        y = random.randint(radius, 600 - radius)
    
    speed = random.uniform(enemy_speed_min + level*0.3, enemy_speed_max + level*0.5)
    img = random.choice(enemy_imgs)
    
    enemies.append({
        'x': x,
        'y': y,
        'radius': radius,
        'speed': speed,
        'direction': random.uniform(0, 2 * math.pi),
        'img': img,
        'direction_change_timer': 0
    })

def spawn_bomb():
    x = random.randint(bomb_radius, 800 - bomb_radius)
    y = random.randint(bomb_radius, 600 - bomb_radius)
    bombs.append({'x': x, 'y': y})

def spawn_laser():
    is_horizontal = random.choice([True, False])
    if is_horizontal:
        y = random.randint(50, 550)
        lasers.append({
            'y': y,
            'horizontal': True,
            'width': laser_width,
            'warning': True,
            'warning_timer': 60,
            'active_timer': 120
        })
    else:
        x = random.randint(50, 750)
        lasers.append({
            'x': x,
            'horizontal': False,
            'width': laser_width,
            'warning': True,
            'warning_timer': 60,
            'active_timer': 120
        })

def reset_game():
    global score, level, food, enemies, bombs, lasers, game_over, game_won
    global player_radius, player_speed, player_x, player_y, invincible, invincible_timer
    
    score = 0
    level = 1
    food = []
    enemies = []
    bombs = []
    lasers = []
    game_over = False
    game_won = False
    player_radius = 20
    player_speed = 3
    player_x = 400
    player_y = 300
    invincible = False
    invincible_timer = 0
    
    for _ in range(50):
        food.append({
            'x': random.randint(food_radius, 800 - food_radius),
            'y': random.randint(food_radius, 600 - food_radius),
            'color': random.choice(food_colors)
        })
    
    for _ in range(5):
        spawn_enemy()
    
    score_to_next_level = 100

# -- Generar comida y enemigos iniciales --
for _ in range(50):
    food.append({
        'x': random.randint(food_radius, 800 - food_radius),
        'y': random.randint(food_radius, 600 - food_radius),
        'color': random.choice(food_colors)
    })

for _ in range(5):
    spawn_enemy()

# --- Bucle principal --
running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (game_over or game_won):
                reset_game()

    if not game_over and not game_won:
        # --Movimiento jugador
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - player_x
        dy = mouse_y - player_y
        distance = max(1, math.hypot(dx, dy))
        player_x += (dx / distance) * player_speed
        player_y += (dy / distance) * player_speed
        player_x = max(player_radius, min(800 - player_radius, player_x))
        player_y = max(player_radius, min(600 - player_radius, player_y))
        
        if invincible:
            invincible_timer -= 1
            if invincible_timer <= 0:
                invincible = False

        # --Comida-
        if random.randint(1, 20) == 1 and len(food) < 100:
            food.append({
                'x': random.randint(food_radius, 800 - food_radius),
                'y': random.randint(food_radius, 600 - food_radius),
                'color': random.choice(food_colors)
            })

        for f in food[:]:
            draw_circle(screen, f['color'], (int(f['x']), int(f['y'])), food_radius)
            if math.hypot(f['x'] - player_x, f['y'] - player_y) < player_radius * 0.9:
                food.remove(f)
                score += 1
                player_radius += 0.2
                player_speed = max(1.5, player_speed - 0.01)
                if score >= score_to_next_level:
                    if level < max_level:
                        start_new_level()
                    else:
                        game_won = True

        # --Bombas en nivel 2+
        if level >= 2:
            if random.randint(1, 200) == 1 and len(bombs) < 5:
                spawn_bomb()

            for bomb in bombs[:]:
                draw_circle(screen, RED, (bomb['x'], bomb['y']), bomb_radius)
                if math.hypot(bomb['x'] - player_x, bomb['y'] - player_y) < player_radius:
                    bombs.remove(bomb)
                    player_radius = max(8, player_radius * 0.7)
                    score = max(0, int(score * 0.8))
                    invincible = True
                    invincible_timer = 60

        # ----Laseres en nivel 3--
        if level >= 3:
            laser_spawn_timer += 1
            if laser_spawn_timer >= 180:
                spawn_laser()
                laser_spawn_timer = 0

            for laser in lasers[:]:
                if laser['warning']:
                    if pygame.time.get_ticks() % 400 < 200:
                        if laser['horizontal']:
                            pygame.draw.line(screen, PINK, (0, laser['y']), (800, laser['y']), 4)
                        else:
                            pygame.draw.line(screen, PINK, (laser['x'], 0), (laser['x'], 600), 4)
                    laser['warning_timer'] -= 1
                    if laser['warning_timer'] <= 0:
                        laser['warning'] = False
                else:
                    if laser['horizontal']:
                        pygame.draw.rect(screen, CYAN, (0, laser['y'] - laser['width']//2, 800, laser['width']))
                        if not invincible and abs(laser['y'] - player_y) < player_radius + laser['width']//2:
                            player_radius = max(8, player_radius * 0.6)
                            score = max(0, int(score * 0.7))
                            invincible = True
                            invincible_timer = 90
                    else:
                        pygame.draw.rect(screen, CYAN, (laser['x'] - laser['width']//2, 0, laser['width'], 600))
                        if not invincible and abs(laser['x'] - player_x) < player_radius + laser['width']//2:
                            player_radius = max(8, player_radius * 0.6)
                            score = max(0, int(score * 0.7))
                            invincible = True
                            invincible_timer = 90

                    laser['active_timer'] -= 1
                    if laser['active_timer'] <= 0:
                        lasers.remove(laser)

        # Enemigos--
        for enemy in enemies[:]:
            enemy['direction_change_timer'] += 1
            if enemy['direction_change_timer'] > 60:
                enemy['direction'] = random.uniform(0, 2 * math.pi)
                enemy['direction_change_timer'] = 0

            enemy['x'] += math.cos(enemy['direction']) * enemy['speed']
            enemy['y'] += math.sin(enemy['direction']) * enemy['speed']
            
            if enemy['x'] < enemy['radius'] or enemy['x'] > 800 - enemy['radius']:
                enemy['direction'] = math.pi - enemy['direction']
            if enemy['y'] < enemy['radius'] or enemy['y'] > 600 - enemy['radius']:
                enemy['direction'] = -enemy['direction']

            draw_image_circle(enemy['img'], enemy['x'], enemy['y'], enemy['radius'])

            collision_distance = (player_radius + enemy['radius']) * 0.72
            if math.hypot(enemy['x'] - player_x, enemy['y'] - player_y) < collision_distance:
                if player_radius > enemy['radius'] * 1.1:
                    enemies.remove(enemy)
                    score += int(enemy['radius'] / 2)
                    player_radius += enemy['radius'] * 0.2
                    player_speed = max(1, player_speed - enemy['radius'] * 0.01)
                    spawn_enemy()
                elif enemy['radius'] > player_radius * 1.1:
                    game_over = True

        # --Dibujar jugador
        if not invincible or pygame.time.get_ticks() % 200 < 100:
            draw_image_circle(player_img, player_x, player_y, int(player_radius))

        # ---Texto
        draw_text(f"Puntuación: {score}", font, BLACK, 100, 30)
        draw_text(f"Nivel: {level}", font, BLACK, 700, 30)
        draw_text(f"Tamaño: {int(player_radius)}", font, BLACK, 400, 30)
        draw_text(f"Siguiente nivel: {score_to_next_level}", font, BLACK, 400, 570)

    if game_over:
        draw_text("GAME OVER", big_font, RED, 400, 250)
        draw_text(f"Puntuación final: {score}", font, BLACK, 400, 320)
        draw_text("Presiona R para reiniciar", font, BLACK, 400, 360)

    if game_won:
        draw_text("¡VICTORIA!", big_font, GREEN, 400, 250)
        draw_text(f"Puntuación final: {score}", font, BLACK, 400, 320)
        draw_text("Presiona R para jugar de nuevo", font, BLACK, 400, 360)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
