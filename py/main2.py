import pygame
from pygame.math import Vector2

pygame.init()

WIDTH, HEIGHT = 640, 640
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stage 1 - Ball Physics")
clock = pygame.time.Clock()

# --- physics constants ---
GRAVITY = 1500.0        # px/s^2, downward acceleration
RESTITUTION = 0.75      # fraction of speed kept after a bounce (0-1)
FRICTION = 0.50          # ground friction damping coefficient
REST_THRESHOLD = 30     # vy below this on floor contact -> treat as settled
RADIUS = 20
COLOR = (235, 90, 90)
BG_COLOR = (15, 15, 20)
START_POS = Vector2(WIDTH / 2, RADIUS)
START_VEL = Vector2(180, 0)

pos = Vector2(START_POS)
vel = Vector2(START_VEL)

font = pygame.font.SysFont("consolas", 18)

running = True
while running:
    # --- delta time ---
    dt = clock.tick(120) / 1000
    dt = max(0.001, min(dt, 0.1))  # clamp so lag spikes don't blow up physics

    # --- events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            pos = Vector2(START_POS)
            vel = Vector2(START_VEL)

    # --- integrate motion ---
    vel.y += GRAVITY * dt
    pos += vel * dt

    on_ground = False

    # floor
    if pos.y + RADIUS >= HEIGHT:
        pos.y = HEIGHT - RADIUS
        vel.y = -vel.y * RESTITUTION
        if abs(vel.y) < REST_THRESHOLD:
            vel.y = 0
        on_ground = True

    # ceiling
    if pos.y - RADIUS <= 0:
        pos.y = RADIUS
        vel.y = -vel.y * RESTITUTION

    # walls
    if pos.x - RADIUS <= 0:
        pos.x = RADIUS
        vel.x = -vel.x * RESTITUTION
    elif pos.x + RADIUS >= WIDTH:
        pos.x = WIDTH - RADIUS
        vel.x = -vel.x * RESTITUTION

    # friction only acts while resting/rolling on the ground
    if on_ground:
        vel.x -= vel.x * FRICTION * dt

    # --- draw ---
    screen.fill(BG_COLOR)
    pygame.draw.circle(screen, COLOR, (int(pos.x), int(pos.y)), RADIUS)

    debug_text = f"pos=({pos.x:6.1f},{pos.y:6.1f})  vel=({vel.x:6.1f},{vel.y:6.1f})  dt={dt:.4f}  [R: reset]"
    screen.blit(font.render(debug_text, True, (200, 200, 200)), (10, 10))

    pygame.display.flip()

pygame.quit()