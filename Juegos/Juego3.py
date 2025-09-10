import pygame
import random
import os
import sys

# -- Inicializacion --
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders Retro")
clock = pygame.time.Clock()

# -- Colores --
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (255, 0, 0)

# -- Paths --
ASSET_PATH = "assets"
FONT_PATH = os.path.join(ASSET_PATH, "fonts", "PressStart2P.ttf")

# - Musica retro de fondo --
pygame.mixer.init()
music_path = os.path.join(ASSET_PATH, "sounds", "retro_music.mp3")
if os.path.exists(music_path):
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.5)  
    pygame.mixer.music.play(-1)  # -1 = loop infinit

# -- Funciones de carga --
def load_img(name, size=None):
    path = os.path.join(ASSET_PATH, name)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

# -- Fuente retro ---
font = pygame.font.Font(FONT_PATH, 20)
big_font = pygame.font.Font(FONT_PATH, 40)

# -- Imágenes ---
player_img = load_img("player_nave.png", (60, 60))

enemy_imgs_lvl1 = [
    load_img("enemy_nave.png", (50, 50)),
    load_img("enemy_nave1.png", (50, 50)),
    load_img("enemy_nave2.png", (50, 50)),
]

enemy_imgs_lvl2 = [
    load_img("enemylvl2_1.png", (50, 50)),
    load_img("enemylvl2_2.png", (50, 50)),
    load_img("enemylvl2_3.png", (50, 50)),
]

boss_img = load_img("halcon.png", (250, 150))
escort_imgs = [
    load_img("final1.png", (60, 60)),
    load_img("final2.png", (60, 60)),
    load_img("final3.png", (60, 60)),
]

vida_img = load_img("vidas.png", (30, 30))

# --- Variables de juego ---
player_x, player_y = 370, 500
player_speed = 5
bullets = []
bullet_speed = -10

enemy_bullets = []
enemy_bullet_speed = 5

enemies = []
enemy_dx = 1.5
enemy_dy = 20
rows, cols = 4, 7

score = 0
lives = 3
level = 1
game_over = False

boss = None
escorts = []
boss_life = 30

# -- Variables de respawn de escoltas ---
escort_respawn_timer = 0
ESCORT_RESPAWN_DELAY = 300  # frames 

# --- Cooldown de disparo del jugador ---
player_cooldown = 0
PLAYER_SHOOT_DELAY = 15  # frames

# ---- Funciones ---
def draw_text(text, font, color, x, y, centered=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if centered else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)

def create_enemy_grid(imgs):
    global enemies
    enemies = []
    for row in range(rows):
        for col in range(cols):
            img = random.choice(imgs)
            x = 100 + col * 80
            y = 50 + row * 60
            enemies.append({"x": x, "y": y, "img": img})

def create_boss():
    global boss, escorts
    boss = {"x": 250, "y": 40, "img": boss_img, "life": boss_life, "dx": 2}
    escorts.clear()
    for row in range(2):
        for i, img in enumerate(escort_imgs):
            escorts.append({
                "x": 150 + i * 150,
                "y": 250 + row * 70,
                "img": img,
                "life": 3,
                "dx": random.choice([-1, 1]) * 1.2
            })

def reset_game():
    global player_x, player_y, bullets, enemies, score, lives, game_over, enemy_dx, level, boss, escorts, escort_respawn_timer, player_cooldown
    player_x, player_y = 370, 500
    bullets = []
    enemy_bullets.clear()
    score = 0
    lives = 3
    game_over = False
    enemy_dx = 1.5
    level = 1
    boss = None
    escorts = []
    escort_respawn_timer = 0
    player_cooldown = 0
    create_enemy_grid(enemy_imgs_lvl1)

# ---- Crear primera oleada --
create_enemy_grid(enemy_imgs_lvl1)

# ---- Bucle principal -
running = True
while running:
    screen.fill(BLACK)

    # --- Cooldown del jugador ----
    if player_cooldown > 0:
        player_cooldown -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                if player_cooldown == 0:
                    bullets.append([player_x + 25, player_y])
                    player_cooldown = PLAYER_SHOOT_DELAY
            if event.key == pygame.K_r and game_over:
                reset_game()

    keys = pygame.key.get_pressed()
    if not game_over:
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < 740:
            player_x += player_speed

    # -- Nivel 1 ----
    if level == 1 and not enemies:
        level = 2
        create_enemy_grid(enemy_imgs_lvl2)

    # -- Nivel 2 ----
    if level == 2 and not enemies:
        level = 3
        create_boss()

    # -- Movimiento enemigos lvl 1 y 2 ----
    if level in [1, 2] and not game_over:
        move_down = False
        for enemy in enemies:
            enemy["x"] += enemy_dx
            if enemy["x"] <= 20 or enemy["x"] >= 730:
                move_down = True
        if move_down:
            enemy_dx *= -1
            for enemy in enemies:
                enemy["y"] += enemy_dy

    # --Dibujar enemigos normales
    if level in [1, 2]:
        for enemy in enemies[:]:
            screen.blit(enemy["img"], (enemy["x"], enemy["y"]))
            if enemy["y"] + 50 >= 500:
                game_over = True
        # --Enemigos que disparan en lvl 2
        if level == 2 and random.randint(1, 50) == 1 and enemies:
            shooter = random.choice(enemies)
            enemy_bullets.append([shooter["x"] + 30, shooter["y"] + 40])

    # ---- Nivel 3 (Jefe Final) --
    if level == 3 and boss and not game_over:
        # mover jefe
        boss["x"] += boss["dx"]
        if boss["x"] <= 50 or boss["x"] + 200 >= 750:
            boss["dx"] *= -1
        screen.blit(boss["img"], (boss["x"], boss["y"]))

        # --jefe dispara varios tiros
        if random.randint(1, 40) == 1:
            for offset in [-40, 0, 40]:
                enemy_bullets.append([boss["x"] + 120 + offset, boss["y"] + 100])

        # --escoltas (naves pequeñas)
        for escort in escorts[:]:
            escort["x"] += escort["dx"]
            if escort["x"] <= 50 or escort["x"] + 50 >= 750:
                escort["dx"] *= -1
            screen.blit(escort["img"], (escort["x"], escort["y"]))
        # -disparo de escoltas
        if escorts and random.randint(1, 80) == 1:
            shooter = random.choice(escorts)
            enemy_bullets.append([shooter["x"] + 20, shooter["y"] + 50])

        # -- Respawn de escoltas --
        if not escorts:
            if escort_respawn_timer == 0:
                escort_respawn_timer = ESCORT_RESPAWN_DELAY
            else:
                escort_respawn_timer -= 1
                if escort_respawn_timer <= 0:
                    escorts = []
                    for row in range(2):
                        for i, img in enumerate(escort_imgs):
                            escorts.append({
                                "x": 150 + i * 150,
                                "y": 250 + row * 70,
                                "img": img,
                                "life": 3,
                                "dx": random.choice([-1, 1]) * 1.2
                            })
                    escort_respawn_timer = 0

    # -- Balas del jugador --
    for bullet in bullets[:]:
        bullet[1] += bullet_speed
        pygame.draw.rect(screen, (255, 255, 0), (bullet[0], bullet[1], 5, 15))
        if bullet[1] < 0:
            bullets.remove(bullet)
            continue

        # -- colisiones con enemigos normales --
        if level in [1, 2]:
            for enemy in enemies[:]:
                ex, ey = enemy["x"], enemy["y"]
                ew, eh = enemy["img"].get_size()
                if (bullet[0] > ex and bullet[0] < ex + ew and
                    bullet[1] > ey and bullet[1] < ey + eh):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10
                    break

        # -- colisiones con jefe --
        if level == 3 and boss:
            bx, by = boss["x"], boss["y"]
            bw, bh = boss["img"].get_size()
            if (bullet[0] > bx and bullet[0] < bx + bw and
                bullet[1] > by and bullet[1] < by + bh):
                bullets.remove(bullet)
                boss["life"] -= 1
                score += 20
                if boss["life"] <= 0:
                    boss = None
                    escorts = []
                    game_over = True  # victoria
                continue
            # colisiones con escoltas
            for escort in escorts[:]:
                ex, ey = escort["x"], escort["y"]
                ew, eh = escort["img"].get_size()
                if (bullet[0] > ex and bullet[0] < ex + ew and
                    bullet[1] > ey and bullet[1] < ey + eh):
                    bullets.remove(bullet)
                    escort["life"] -= 1
                    if escort["life"] <= 0:
                        escorts.remove(escort)
                    score += 15
                    break

    # ---- Balas enemigas ----
    for e_bullet in enemy_bullets[:]:
        e_bullet[1] += enemy_bullet_speed
        pygame.draw.rect(screen, RED, (e_bullet[0], e_bullet[1], 5, 15))
        if e_bullet[1] > 600:
            enemy_bullets.remove(e_bullet)
            continue
        if (player_x < e_bullet[0] < player_x + 60 and
            player_y < e_bullet[1] < player_y + 60):
            enemy_bullets.remove(e_bullet)
            lives -= 1
            if lives <= 0:
                game_over = True

    # -- Dibujar jugador --
    if not game_over:
        screen.blit(player_img, (player_x, player_y))

    # -- HUD --
    draw_text(f"Puntos: {score}", font, WHITE, 10, 10)
    draw_text(f"Nivel: {level}", font, WHITE, 650, 10)
    for i in range(lives):
        screen.blit(vida_img, (10 + i * 35, 50))

    # --- GAME OVER ---
    if game_over:
        msg = "VICTORIA!" if boss is None and level == 3 else "GAME OVER"
        draw_text(msg, big_font, RED, 400, 250, True)
        draw_text("Presiona R para reiniciar", font, WHITE, 400, 320, True)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
