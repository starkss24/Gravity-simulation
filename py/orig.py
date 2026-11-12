import pygame
from pygame.math import Vector2

pygame.init()

screen = pygame.display.set_mode((640, 640))

potato_img = pygame.image.load("py/images/potato.jpg").convert_alpha()

potato_img = pygame.transform.scale(potato_img, (30, 30))

potato_img.set_colorkey((255, 255, 255))
potato_img.set_colorkey((230, 230, 230))

x = 30
y = 30
delta_time = 0.1

position = Vector2(30,30)
velocity = Vector2(100,0)
acceleration = Vector2(0,0)

clock = pygame.time.Clock()
running = True

vx= 100
ax = 100
fx = 0.01 
while running:
    screen.fill((0,0,0))
    # circle = pygame.draw.circle(screen, (255,255,255), (30,x), 20)
    pygame.draw.rect(screen, (255, 0, 0), (x, y, 50, 50))
    
    # screen.blit(potato_img, (x,30))
    # screen.blit(circle, (30,30))

    position += velocity * delta_time  
    velocity -= velocity*fx*delta_time

    if x + 50 >= 640:
        x = 640-50
        vx = -vx
    elif x <= 0:
        x = 0
        vx = -vx

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        vx += ax * delta_time
    if keys[pygame.K_a]:
        vx -= ax * delta_time
    # if(x+50 > screen.width):
    #       vx = -vx

    # if keys[pygame.K_w]:
    #         y -= vx*delta_time

    # if keys[pygame.K_s]:
    #         y += vx*delta_time

    # if keys[pygame.K_a]: 
    #         x -= vx*delta_time

    # if keys[pygame.K_d]:
    #         x += vx*10*delta_time

    pygame.display.flip()
    delta_time = clock.tick(120)/1000
    delta_time = max( 0.001, min(delta_time, 0.1))

pygame.quit()