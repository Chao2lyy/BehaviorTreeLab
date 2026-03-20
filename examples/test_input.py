import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pygame

pygame.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("按键测试")

clock = pygame.time.Clock()
FPS = 60

font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)

player_x, player_y = 400, 300
player_speed = 5

running = True
while running:
    screen.fill((0, 0, 0))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    keys = pygame.key.get_pressed()
    
    key_text = []
    if keys[pygame.K_w]:
        key_text.append("W")
        player_y -= player_speed
    if keys[pygame.K_s]:
        key_text.append("S")
        player_y += player_speed
    if keys[pygame.K_a]:
        key_text.append("A")
        player_x -= player_speed
    if keys[pygame.K_d]:
        key_text.append("D")
        player_x += player_speed
    if keys[pygame.K_SPACE]:
        key_text.append("SPACE")
    
    player_x = max(30, min(WINDOW_WIDTH - 30, player_x))
    player_y = max(30, min(WINDOW_HEIGHT - 30, player_y))
    
    pygame.draw.circle(screen, (0, 255, 0), (player_x, player_y), 25)
    
    if key_text:
        text = font_large.render("按下: " + " ".join(key_text), True, (255, 255, 0))
        screen.blit(text, (50, 50))
    else:
        text = font_large.render("请按 WASD 或空格键", True, (255, 255, 255))
        screen.blit(text, (50, 50))
    
    instruction = font_small.render("WASD - 移动 | SPACE - 攻击", True, (200, 200, 200))
    screen.blit(instruction, (50, 120))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
