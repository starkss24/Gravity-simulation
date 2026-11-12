import math
import random

import pygame
from pygame.math import Vector2

pygame.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("N-Body Gravity")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 16)

G = 8000.0          
SOFTENING = 8.0      
WALL_RESTITUTION = 0.85
BG_COLOR = (8, 8, 14)
SUN_COLOR = (255, 190, 60)

TRAIL_FADE = 2       
TRAIL_DOT_SCALE = 0.35  

trail_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)


class Ball:
    def __init__(self, pos, vel, mass, fixed=False):
        self.pos = Vector2(pos)
        self.vel = Vector2(vel)
        self.mass = mass
        self.fixed = fixed  
        self.radius = max(4, int(mass ** (1 / 3) * 3))
        self.color = (
            random.randint(80, 255),
            random.randint(80, 255),
            random.randint(80, 255),
        )

    def apply_force(self, force, dt):
        if self.fixed:
            return
        self.vel += (force / self.mass) * dt

    def update(self, dt):
        if self.fixed:
            return
        self.pos += self.vel * dt
        self._bounce_off_walls()

    def _bounce_off_walls(self):
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.vel.x = -self.vel.x * WALL_RESTITUTION
        elif self.pos.x + self.radius > WIDTH:
            self.pos.x = WIDTH - self.radius
            self.vel.x = -self.vel.x * WALL_RESTITUTION
        if self.pos.y - self.radius < 0:
            self.pos.y = self.radius
            self.vel.y = -self.vel.y * WALL_RESTITUTION
        elif self.pos.y + self.radius > HEIGHT:
            self.pos.y = HEIGHT - self.radius
            self.vel.y = -self.vel.y * WALL_RESTITUTION

    def draw_trail_dot(self, surf):
        r = max(1, int(self.radius * TRAIL_DOT_SCALE))
        pygame.draw.circle(surf, (*self.color, 255), (int(self.pos.x), int(self.pos.y)), r)

    def draw(self, surf):
        pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


def gravity_force(a, b):
    """Newtonian attraction pulling `a` toward `b`: F = G*m1*m2 / r^2."""
    delta = b.pos - a.pos
    dist_sq = delta.length_squared()
    if dist_sq == 0:
        return Vector2(0, 0)
    softened_dist_sq = dist_sq + SOFTENING ** 2
    force_mag = G * a.mass * b.mass / softened_dist_sq
    return delta.normalize() * force_mag

def make_sun():
    sun = Ball((WIDTH / 2, HEIGHT / 2), (0, 0), 400, fixed=True)
    sun.color = SUN_COLOR
    return sun

def orbital_velocity(spawn_pos, center_body):
    """Tangential velocity that gives a (roughly) circular orbit around
    center_body, based on v = sqrt(G * M / r)."""
    to_ball = spawn_pos - center_body.pos
    dist = to_ball.length()
    if dist < 1:
        dist = 1
        to_ball = Vector2(1, 0)
    speed = math.sqrt(G * center_body.mass / dist)
    tangent = to_ball.normalize().rotate(90)
    return tangent * speed


sun = make_sun()
balls = [sun]

running = True
while running:
    dt = clock.tick(120) / 1000
    dt = max(0.0005, min(dt, 0.05))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mass = 400  # match the sun's mass
            spawn_pos = Vector2(event.pos)
            vel = orbital_velocity(spawn_pos, sun)
            balls.append(Ball(spawn_pos, vel, mass))
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            sun = make_sun()
            balls = [sun]
            trail_surface.fill((0, 0, 0, 0))  

    for i, a in enumerate(balls):
        if a.fixed:
            continue
        net_force = Vector2(0, 0)
        for j, b in enumerate(balls):
            if i != j:
                net_force += gravity_force(a, b)
        a.apply_force(net_force, dt)

    for ball in balls:
        ball.update(dt)

    trail_surface.fill((0, 0, 0, TRAIL_FADE), special_flags=pygame.BLEND_RGBA_SUB)
    for ball in balls:
        if not ball.fixed:
            ball.draw_trail_dot(trail_surface)

    screen.fill(BG_COLOR)
    screen.blit(trail_surface, (0, 0))
    for ball in balls:
        ball.draw(screen)

    info = f"balls={len(balls)}  fps={clock.get_fps():.0f}  [click: spawn]  [R: reset]"
    screen.blit(font.render(info, True, (200, 200, 200)), (10, 10))

    pygame.display.flip()

pygame.quit()