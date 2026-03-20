import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pygame
import math
from typing import List
from behavior_tree import Blackboard
from ai_teammate.entities import Player, Teammate, Enemy, Vector2
from ai_teammate.ai_behavior import AITeammate


class GameGUI:
    """AI队友行为树图形化游戏界面"""
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        
        self.WINDOW_WIDTH = 1000
        self.WINDOW_HEIGHT = 700
        self.GAME_AREA_WIDTH = 750
        self.GAME_AREA_HEIGHT = 700
        self.UI_WIDTH = 250
        self.UI_HEIGHT = 700
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("AI Teammate Behavior Tree")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        self.running = True
        self.game_paused = False
        self.game_started = False
        self.game_over = False
        self.debug_keys = []
        
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'dark_gray': (64, 64, 64),
            'light_gray': (200, 200, 200),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'cyan': (0, 255, 255),
            'pink': (255, 192, 203)
        }
        
        self.load_fonts()
        self.init_game()
        
    def load_fonts(self):
        """加载字体"""
        font_paths = [
            "C:\\Windows\\Fonts\\msyh.ttc",
            "C:\\Windows\\Fonts\\simhei.ttf",
            "C:\\Windows\\Fonts\\simsun.ttc"
        ]
        
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    try:
                        self.font_large = pygame.font.Font(font_path, 28)
                        self.font_medium = pygame.font.Font(font_path, 22)
                        self.font_small = pygame.font.Font(font_path, 16)
                        break
                    except:
                        continue
            except:
                continue
        
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 22)
            self.font_small = pygame.font.Font(None, 16)
        
    def init_game(self):
        """初始化游戏实体"""
        self.blackboard = Blackboard()
        self.game_over = False
        self.game_started = False
        
        self.player = Player(Vector2(300, 300))
        self.teammate = Teammate("AI Teammate", Vector2(350, 350))
        self.enemies: List[Enemy] = []
        
        self.enemies.append(Enemy("Enemy 1", Vector2(600, 200), 50))
        self.enemies.append(Enemy("Enemy 2", Vector2(650, 500), 50))
        self.enemies.append(Enemy("Enemy 3", Vector2(200, 550), 50))
        
        self.ai_teammate = AITeammate(self.teammate, self.player, self.blackboard)
        for enemy in self.enemies:
            self.ai_teammate.add_enemy(enemy)
        
        self.player_speed = 4.0
        self.teammate_speed = 2.5
        self.enemy_speed = 1.5
        
        self.attack_cooldown = 0
        self.enemy_attack_cooldowns = {enemy: 0 for enemy in self.enemies}
        
        self.attack_range = 80.0
        self.attack_damage = 20.0
        self.enemy_attack_range = 60.0
        self.enemy_attack_damage = 10.0
        
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)
        
        keys = pygame.key.get_pressed()
        self.handle_player_input(keys)
        
    def handle_player_input(self, keys):
        """处理玩家输入"""
        if self.game_paused or not self.player.is_alive or self.game_over or not self.game_started:
            return
            
        self.debug_keys = []
        
        dx, dy = 0, 0
        
        if keys[pygame.K_w]:
            dy = -1
            self.debug_keys.append("W")
        if keys[pygame.K_s]:
            dy = 1
            self.debug_keys.append("S")
        if keys[pygame.K_a]:
            dx = -1
            self.debug_keys.append("A")
        if keys[pygame.K_d]:
            dx = 1
            self.debug_keys.append("D")
        if keys[pygame.K_UP]:
            dy = -1
            self.debug_keys.append("UP")
        if keys[pygame.K_DOWN]:
            dy = 1
            self.debug_keys.append("DOWN")
        if keys[pygame.K_LEFT]:
            dx = -1
            self.debug_keys.append("LEFT")
        if keys[pygame.K_RIGHT]:
            dx = 1
            self.debug_keys.append("RIGHT")
        
        if dx != 0 or dy != 0:
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            new_x = self.player.position.x + dx * self.player_speed
            new_y = self.player.position.y + dy * self.player_speed
            
            new_x = max(30, min(self.GAME_AREA_WIDTH - 30, new_x))
            new_y = max(30, min(self.GAME_AREA_HEIGHT - 30, new_y))
            
            self.player.position = Vector2(new_x, new_y)
        
        if keys[pygame.K_SPACE]:
            self.debug_keys.append("SPACE")
            if self.attack_cooldown <= 0:
                self.player_attack()
                self.attack_cooldown = 30
            
    def player_attack(self):
        """玩家攻击"""
        for enemy in self.enemies:
            if enemy.is_alive:
                dist = self.player.position.distance_to(enemy.position)
                if dist < self.attack_range:
                    enemy.take_damage(self.attack_damage)
                    self.player.look_at(enemy.position)
                    
    def handle_mouse_click(self, pos):
        """处理鼠标点击"""
        x, y = pos
        if x > self.GAME_AREA_WIDTH:
            ui_x = x - self.GAME_AREA_WIDTH
            ui_y = y
            
            if not self.game_started and 50 <= ui_x <= 200 and 150 <= ui_y <= 190:
                self.start_game()
            elif self.game_started and 50 <= ui_x <= 200 and 150 <= ui_y <= 190:
                self.toggle_pause()
            elif self.game_started and 50 <= ui_x <= 200 and 210 <= ui_y <= 250:
                self.restart_game()
                
    def start_game(self):
        """开始游戏"""
        self.game_started = True
        self.game_paused = False
        
    def toggle_pause(self):
        """暂停/继续游戏"""
        self.game_paused = not self.game_paused
        
    def restart_game(self):
        """重新开始游戏"""
        self.game_paused = False
        self.game_started = False
        self.init_game()
        
    def update(self):
        """更新游戏状态"""
        if self.game_paused or self.game_over or not self.game_started:
            return
            
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        for enemy in self.enemies:
            if self.enemy_attack_cooldowns[enemy] > 0:
                self.enemy_attack_cooldowns[enemy] -= 1
                
        self.update_enemies()
        
        if self.teammate.is_alive:
            self.ai_teammate.update()
        
        self.check_game_over()
        
    def check_game_over(self):
        """检查游戏是否结束"""
        if not self.player.is_alive:
            self.game_over = True
            return
            
        all_enemies_dead = all(not enemy.is_alive for enemy in self.enemies)
        if all_enemies_dead:
            self.game_over = True
        
    def update_enemies(self):
        """更新敌人AI"""
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
                
            targets = []
            if self.player.is_alive:
                targets.append((self.player, self.player.position.distance_to(enemy.position)))
            if self.teammate.is_alive:
                targets.append((self.teammate, self.teammate.position.distance_to(enemy.position)))
                
            if not targets:
                continue
                
            targets.sort(key=lambda x: x[1])
            target, dist = targets[0]
            
            if dist < self.enemy_attack_range:
                if self.enemy_attack_cooldowns[enemy] <= 0:
                    target.take_damage(self.enemy_attack_damage)
                    self.enemy_attack_cooldowns[enemy] = 60
                    enemy.look_at(target.position)
            else:
                direction = target.position - enemy.position
                direction = direction.normalized()
                new_x = enemy.position.x + direction.x * self.enemy_speed
                new_y = enemy.position.y + direction.y * self.enemy_speed
                
                new_x = max(30, min(self.GAME_AREA_WIDTH - 30, new_x))
                new_y = max(30, min(self.GAME_AREA_HEIGHT - 30, new_y))
                
                enemy.position = Vector2(new_x, new_y)
                enemy.look_at(target.position)
                
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(self.colors['dark_gray'])
        
        self.draw_game_area()
        self.draw_ui_panel()
        
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
        
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(self.colors['black'])
        self.screen.blit(overlay, (0, 0))
        
        if not self.player.is_alive:
            title_text = "Game Over - You Died!"
            title_color = self.colors['red']
        else:
            title_text = "Victory - All Enemies Defeated!"
            title_color = self.colors['green']
        
        title_surface = self.font_large.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(title_surface, title_rect)
        
        restart_text = "Press Restart to play again"
        restart_surface = self.font_medium.render(restart_text, True, self.colors['white'])
        restart_rect = restart_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(restart_surface, restart_rect)
        
    def draw_game_area(self):
        """绘制游戏区域"""
        game_surface = pygame.Surface((self.GAME_AREA_WIDTH, self.GAME_AREA_HEIGHT))
        game_surface.fill(self.colors['light_gray'])
        
        for x in range(0, self.GAME_AREA_WIDTH, 50):
            pygame.draw.line(game_surface, self.colors['gray'], (x, 0), (x, self.GAME_AREA_HEIGHT))
        for y in range(0, self.GAME_AREA_HEIGHT, 50):
            pygame.draw.line(game_surface, self.colors['gray'], (0, y), (self.GAME_AREA_WIDTH, y))
        
        if self.debug_keys:
            debug_text = "Keys: " + " ".join(self.debug_keys)
            text_surface = self.font_medium.render(debug_text, True, self.colors['blue'])
            game_surface.blit(text_surface, (10, 10))
            
        for enemy in self.enemies:
            if enemy.is_alive:
                self.draw_character(game_surface, enemy, self.colors['red'], self.colors['dark_gray'])
            else:
                self.draw_dead_character(game_surface, enemy, self.colors['red'])
                
        if self.teammate.is_alive:
            self.draw_character(game_surface, self.teammate, self.colors['cyan'], self.colors['blue'])
        else:
            self.draw_dead_character(game_surface, self.teammate, self.colors['cyan'])
            
        if self.player.is_alive:
            self.draw_character(game_surface, self.player, self.colors['green'], self.colors['dark_gray'])
        else:
            self.draw_dead_character(game_surface, self.player, self.colors['green'])
            
        self.screen.blit(game_surface, (0, 0))
        
    def draw_character(self, surface, character, body_color, outline_color):
        """绘制角色"""
        x = int(character.position.x)
        y = int(character.position.y)
        radius = 25
        
        pygame.draw.circle(surface, body_color, (x, y), radius)
        pygame.draw.circle(surface, outline_color, (x, y), radius, 3)
        
        eye_offset = 8
        eye_radius = 4
        angle = character.rotation
        eye1_x = x + int(math.cos(angle) * eye_offset - math.sin(angle) * 5)
        eye1_y = y + int(math.sin(angle) * eye_offset + math.cos(angle) * 5)
        eye2_x = x + int(math.cos(angle) * eye_offset + math.sin(angle) * 5)
        eye2_y = y + int(math.sin(angle) * eye_offset - math.cos(angle) * 5)
        
        pygame.draw.circle(surface, self.colors['white'], (eye1_x, eye1_y), eye_radius)
        pygame.draw.circle(surface, self.colors['white'], (eye2_x, eye2_y), eye_radius)
        pygame.draw.circle(surface, self.colors['black'], (eye1_x, eye1_y), 2)
        pygame.draw.circle(surface, self.colors['black'], (eye2_x, eye2_y), 2)
        
        self.draw_health_bar(surface, character, x, y - radius - 15)
        self.draw_name(surface, character, x, y - radius - 30)
        
    def draw_dead_character(self, surface, character, color):
        """绘制死亡角色"""
        x = int(character.position.x)
        y = int(character.position.y)
        radius = 25
        
        pygame.draw.circle(surface, self.colors['gray'], (x, y), radius)
        pygame.draw.line(surface, color, (x - 10, y - 10), (x + 10, y + 10), 3)
        pygame.draw.line(surface, color, (x + 10, y - 10), (x - 10, y + 10), 3)
        
    def draw_health_bar(self, surface, character, x, y):
        """绘制血条"""
        bar_width = 50
        bar_height = 8
        fill_width = int(bar_width * character.hp_percentage())
        
        pygame.draw.rect(surface, self.colors['black'], (x - bar_width // 2 - 1, y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(surface, self.colors['red'], (x - bar_width // 2, y, bar_width, bar_height))
        pygame.draw.rect(surface, self.colors['green'], (x - bar_width // 2, y, fill_width, bar_height))
        
    def draw_name(self, surface, character, x, y):
        """绘制角色名称"""
        text = self.font_small.render(character.name, True, self.colors['black'])
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)
        
    def draw_ui_panel(self):
        """绘制UI面板"""
        ui_surface = pygame.Surface((self.UI_WIDTH, self.UI_HEIGHT))
        ui_surface.fill(self.colors['black'])
        
        title = self.font_large.render("AI Teammate", True, self.colors['white'])
        ui_surface.blit(title, (30, 20))
        
        self.draw_status_section(ui_surface, 70)
        self.draw_buttons(ui_surface)
        self.draw_controls(ui_surface, 380)
        self.draw_legend(ui_surface, 480)
        
        self.screen.blit(ui_surface, (self.GAME_AREA_WIDTH, 0))
        
    def draw_status_section(self, surface, y_offset):
        """绘制状态信息区域"""
        section_title = self.font_medium.render("Status", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        y = y_offset + 40
        
        player_text = f"Player: {self.player.hp:.0f}/{self.player.max_hp:.0f}"
        player_color = self.colors['green'] if self.player.is_alive else self.colors['gray']
        surface.blit(self.font_small.render(player_text, True, player_color), (20, y))
        y += 25
        
        teammate_text = f"AI: {self.teammate.hp:.0f}/{self.teammate.max_hp:.0f}"
        teammate_color = self.colors['cyan'] if self.teammate.is_alive else self.colors['gray']
        surface.blit(self.font_small.render(teammate_text, True, teammate_color), (20, y))
        y += 25
        
        behavior_text = f"Action: {self.teammate.current_behavior}"
        surface.blit(self.font_small.render(behavior_text, True, self.colors['orange']), (20, y))
        y += 25
        
        potion_text = f"Potions: {self.teammate.healing_potion_count}"
        surface.blit(self.font_small.render(potion_text, True, self.colors['pink']), (20, y))
        y += 35
        
        enemy_count = sum(1 for e in self.enemies if e.is_alive)
        enemy_text = f"Enemies: {enemy_count}/{len(self.enemies)}"
        surface.blit(self.font_small.render(enemy_text, True, self.colors['red']), (20, y))
        
    def draw_buttons(self, surface):
        """绘制控制按钮"""
        buttons = []
        
        if not self.game_started:
            buttons.append(("Start Game", self.colors['green'], 150))
        else:
            pause_text = "Resume" if self.game_paused else "Pause"
            pause_color = self.colors['orange'] if self.game_paused else self.colors['yellow']
            buttons.append((pause_text, pause_color, 150))
            buttons.append(("Restart", self.colors['blue'], 210))
        
        for text, color, y_pos in buttons:
            self.draw_button(surface, text, 50, y_pos, 150, 40, color)
            
    def draw_button(self, surface, text, x, y, width, height, color):
        """绘制单个按钮"""
        pygame.draw.rect(surface, color, (x, y, width, height))
        pygame.draw.rect(surface, self.colors['white'], (x, y, width, height), 2)
        
        text_surface = self.font_medium.render(text, True, self.colors['black'])
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        surface.blit(text_surface, text_rect)
        
    def draw_controls(self, surface, y_offset):
        """绘制操作说明"""
        title = self.font_medium.render("Controls", True, self.colors['yellow'])
        surface.blit(title, (20, y_offset))
        
        controls = [
            ("WASD/Arrows", "Move"),
            ("SPACE", "Attack")
        ]
        
        y = y_offset + 35
        for key, action in controls:
            key_text = self.font_small.render(key, True, self.colors['cyan'])
            action_text = self.font_small.render(f"- {action}", True, self.colors['white'])
            surface.blit(key_text, (20, y))
            surface.blit(action_text, (140, y))
            y += 25
            
    def draw_legend(self, surface, y_offset):
        """绘制图例"""
        title = self.font_medium.render("Legend", True, self.colors['yellow'])
        surface.blit(title, (20, y_offset))
        
        legends = [
            ("Green", "Player", self.colors['green']),
            ("Cyan", "AI Teammate", self.colors['cyan']),
            ("Red", "Enemy", self.colors['red'])
        ]
        
        y = y_offset + 45
        for name, desc, color in legends:
            pygame.draw.circle(surface, color, (35, y), 10)
            text = self.font_small.render(f"{name} - {desc}", True, self.colors['white'])
            surface.blit(text, (55, y - 8))
            y += 30
            
    def run(self):
        """游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.FPS)
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GameGUI()
    game.run()
