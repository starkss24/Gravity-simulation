import math
import random

import pygame
from pygame.math import Vector3

pygame.init()

WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-Body Gravity (3D)")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)

G = 6000.0            # tuned gravitational constant (pixel units, not SI)
SOFTENING = 8.0        # prevents force -> infinity as distance -> 0
WALL_RESTITUTION = 0.85
BG_COLOR = (8, 8, 14)

# World is a 3D box centered on the origin (0,0,0). x/y roughly match the
# screen size, z gives depth for balls to move "into"/"out of" the screen.
WORLD_HALF = Vector3(WIDTH / 2, HEIGHT / 2, 400)

# Camera sits CAM_DISTANCE behind the world origin, looking along +z.
# FOCAL_LENGTH controls zoom / field of view (bigger = more zoomed in).
CAM_DISTANCE = 900
FOCAL_LENGTH = 700

# Current scene rotation, changed by right-click-dragging the mouse.
rot_y = 0.0   # spin around vertical axis (left/right drag)
rot_x = 0.0   # tilt around horizontal axis (up/down drag)


class Ball:
    def __init__(self, pos, vel, mass):
        self.pos = Vector3(pos)
        self.vel = Vector3(vel)
        self.mass = mass
        self.radius = max(4, int(mass ** (1 / 3) * 3))
        self.color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255),
        )

    def apply_force(self, force, dt):
        self.vel += (force / self.mass) * dt

    def update(self, dt):
        self.pos += self.vel * dt
        self._bounce_off_walls()

    def _bounce_off_walls(self):
        # Same reflect-and-damp logic as the 2D version, just run over x, y, z.
        for axis in ("x", "y", "z"):
            half = getattr(WORLD_HALF, axis)
            p = getattr(self.pos, axis)
            v = getattr(self.vel, axis)
            if p - self.radius < -half:
                setattr(self.pos, axis, -half + self.radius)
                setattr(self.vel, axis, -v * WALL_RESTITUTION)
            elif p + self.radius > half:
                setattr(self.pos, axis, half - self.radius)
                setattr(self.vel, axis, -v * WALL_RESTITUTION)

    def projected(self):
        """Rotate this ball's position around the scene center according to
        the current camera rotation, then perspective-project it to 2D
        screen coordinates. Returns None if the point is behind the camera."""
        p = self.pos.rotate(math.degrees(rot_y), Vector3(0, 1, 0))
        p = p.rotate(math.degrees(rot_x), Vector3(1, 0, 0))
        z_cam = p.z + CAM_DISTANCE
        if z_cam <= 1:
            return None
        scale = FOCAL_LENGTH / z_cam
        sx = WIDTH / 2 + p.x * scale
        sy = HEIGHT / 2 + p.y * scale
        return sx, sy, scale, p.z


def gravity_force(a, b):
    """Newtonian attraction pulling `a` toward `b`: F = G*m1*m2 / r^2."""
    delta = b.pos - a.pos
    dist_sq = delta.length_squared()
    if dist_sq == 0:
        return Vector3(0, 0, 0)
    softened_dist_sq = dist_sq + SOFTENING ** 2
    force_mag = G * a.mass * b.mass / softened_dist_sq
    return delta.normalize() * force_mag


# start with one heavy "sun" at the center; click to add orbiting bodies
balls = [Ball((0, 0, 0), (0, 0, 0), 400)]

dragging = False
last_mouse = (0, 0)

running = True
while running:
    dt = clock.tick(120) / 1000
    dt = max(0.0005, min(dt, 0.05))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Left click: spawn a ball. It starts at the screen-space
                # x/y you clicked (converted into world space) with a
                # random depth so new balls don't all line up at z=0.
                mass = random.uniform(5, 30)
                wx = event.pos[0] - WIDTH / 2
                wy = event.pos[1] - HEIGHT / 2
                wz = random.uniform(-150, 150)
                balls.append(Ball((wx, wy, wz), (0, 0, 0), mass))
            elif event.button == 3:
                dragging = True
                last_mouse = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            dx = event.pos[0] - last_mouse[0]
            dy = event.pos[1] - last_mouse[1]
            rot_y += dx * 0.01
            rot_x += dy * 0.01
            last_mouse = event.pos

        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            balls = [Ball((0, 0, 0), (0, 0, 0), 400)]
            rot_y = rot_x = 0.0

    # --- N-body gravity: every ball pulls on every other ball (unchanged) ---
    for i, a in enumerate(balls):
        net_force = Vector3(0, 0, 0)
        for j, b in enumerate(balls):
            if i != j:
                net_force += gravity_force(a, b)
        a.apply_force(net_force, dt)

    for ball in balls:
        ball.update(dt)

    screen.fill(BG_COLOR)

    # Project every ball once, drop any that are behind the camera, then
    # paint back-to-front (painter's algorithm) so nearer balls correctly
    # overlap farther ones.
    projected = []
    for ball in balls:
        proj = ball.projected()
        if proj is not None:
            projected.append((proj[3], ball, proj))
    projected.sort(key=lambda t: t[0], reverse=True)  # farthest first

    for depth, ball, (sx, sy, scale, _) in projected:
        r = max(1, int(ball.radius * scale))
        shade = max(0.35, min(1.0, scale))  # dim distant balls slightly
        color = tuple(int(c * shade) for c in ball.color)
        pygame.draw.circle(screen, color, (int(sx), int(sy)), r)

    info = (
        f"balls={len(balls)}  fps={clock.get_fps():.0f}  "
        f"[left-click: spawn]  [right-drag: rotate]  [R: reset]"
    )
    screen.blit(font.render(info, True, (200, 200, 200)), (10, 10))

    pygame.display.flip()

pygame.quit()