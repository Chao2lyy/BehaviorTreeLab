import sys
import os
import random
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pygame
import math
from typing import List
from behavior_tree import Blackboard
from ai_teammate.entities import Player, Teammate, Enemy, Vector2
from ai_teammate.ai_behavior import AITeammate
from ai_teammate.config import GameConfig
from ai_teammate.score_manager import ScoreManager


class HealthPack:
    """血包类"""
    
    def __init__(self, position: Vector2, heal_amount: float):
        self.position = position
        self.heal_amount = heal_amount
        self.radius = 15


class GameGUIEnhanced:
    """AI队友行为树图形化游戏界面 - 增强版"""
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        
        self.config = GameConfig()
        self.score_manager = ScoreManager(self.config)
        
        self.WINDOW_WIDTH = 1100
        self.WINDOW_HEIGHT = 700
        self.GAME_AREA_WIDTH = 750
        self.GAME_AREA_HEIGHT = 700
        self.UI_WIDTH = 350
        self.UI_HEIGHT = 700
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("AI Teammate - Enhanced")
        
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
            'pink': (255, 192, 203),
            'purple': (128, 0, 128)
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
        self.score_manager.reset_current_score()
        
        self.enemy_spawn_timer = 0
        
        self.player = Player(Vector2(300, 300))
        self.player.max_hp = self.config.player.max_hp
        self.player.hp = self.config.player.max_hp
        
        self.teammate = Teammate("AI Teammate", Vector2(350, 350))
        self.teammate.max_hp = self.config.teammate.max_hp
        self.teammate.hp = self.config.teammate.max_hp
        self.teammate.healing_potion_count = self.config.teammate.healing_potion_count
        
        self.enemies: List[Enemy] = []
        self.health_packs: List[HealthPack] = []
        
        self.ai_teammate = AITeammate(self.teammate, self.player, self.blackboard, self.config.teammate)
        
        self.player_speed = self.config.player.speed
        self.attack_cooldown = 0
        self.enemy_attack_cooldowns = {}
        
        self.attack_range = self.config.player.attack_range
        self.attack_damage = self.config.player.attack_damage
        
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
                self.attack_cooldown = self.config.player.attack_cooldown
            
    def player_attack(self):
        """玩家攻击"""
        for enemy in self.enemies:
            if enemy.is_alive:
                dist = self.player.position.distance_to(enemy.position)
                if dist < self.attack_range:
                    enemy.take_damage(self.attack_damage)
                    self.player.look_at(enemy.position)
                    if not enemy.is_alive:
                        self.score_manager.add_score(self.config.score.player_kill_score)
                    
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
            if enemy in self.enemy_attack_cooldowns and self.enemy_attack_cooldowns[enemy] > 0:
                self.enemy_attack_cooldowns[enemy] -= 1
                
        self.update_enemies()
        self.spawn_enemies()
        self.spawn_health_packs()
        self.check_health_pack_pickup()
        
        if self.teammate.is_alive:
            self.ai_teammate.update()
            self.check_ai_kills()
        
        self.check_game_over()
        
    def check_ai_kills(self):
        """检查AI击杀的敌人"""
        for enemy in self.enemies:
            if not enemy.is_alive and hasattr(enemy, 'counted_for_score'):
                if not enemy.counted_for_score:
                    enemy.counted_for_score = True
                    self.score_manager.add_score(self.config.score.teammate_kill_score)
                    
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
            
            if dist < self.config.enemy.attack_range:
                if enemy not in self.enemy_attack_cooldowns or self.enemy_attack_cooldowns[enemy] <= 0:
                    target.take_damage(self.config.enemy.attack_damage)
                    self.enemy_attack_cooldowns[enemy] = self.config.enemy.attack_cooldown
                    enemy.look_at(target.position)
            else:
                direction = target.position - enemy.position
                direction = direction.normalized()
                new_x = enemy.position.x + direction.x * self.config.enemy.speed
                new_y = enemy.position.y + direction.y * self.config.enemy.speed
                
                new_x = max(30, min(self.GAME_AREA_WIDTH - 30, new_x))
                new_y = max(30, min(self.GAME_AREA_HEIGHT - 30, new_y))
                
                enemy.position = Vector2(new_x, new_y)
                enemy.look_at(target.position)
        
        self.enemies = [e for e in self.enemies if e.is_alive]
        
    def spawn_enemies(self):
        """敌人生成"""
        self.enemy_spawn_timer += 1
        
        if len(self.enemies) < self.config.spawn.max_enemies:
            if self.enemy_spawn_timer >= self.config.spawn.spawn_interval:
                self.enemy_spawn_timer = 0
                
                x = random.uniform(self.config.spawn.min_spawn_x, self.config.spawn.max_spawn_x)
                y = random.uniform(self.config.spawn.min_spawn_y, self.config.spawn.max_spawn_y)
                
                enemy = Enemy(f"Enemy {len(self.enemies) + 1}", Vector2(x, y), self.config.enemy.max_hp)
                enemy.counted_for_score = False
                self.enemies.append(enemy)
                self.ai_teammate.add_enemy(enemy)
                self.enemy_attack_cooldowns[enemy] = 0
                
    def spawn_health_packs(self):
        """血包生成"""
        if len(self.health_packs) < self.config.health_pack.max_packs:
            if random.random() < self.config.health_pack.spawn_chance:
                x = random.uniform(50, self.GAME_AREA_WIDTH - 50)
                y = random.uniform(50, self.GAME_AREA_HEIGHT - 50)
                self.health_packs.append(HealthPack(Vector2(x, y), self.config.health_pack.heal_amount))
                
    def check_health_pack_pickup(self):
        """检查血包拾取"""
        packs_to_remove = []
        
        for pack in self.health_packs:
            if self.player.is_alive:
                dist = self.player.position.distance_to(pack.position)
                if dist < self.config.health_pack.pickup_range:
                    self.player.heal(pack.heal_amount)
                    packs_to_remove.append(pack)
                    continue
                    
            if self.teammate.is_alive:
                dist = self.teammate.position.distance_to(pack.position)
                if dist < self.config.health_pack.pickup_range:
                    self.teammate.heal(pack.heal_amount)
                    packs_to_remove.append(pack)
                    
        for pack in packs_to_remove:
            if pack in self.health_packs:
                self.health_packs.remove(pack)
        
    def check_game_over(self):
        """检查游戏是否结束"""
        if not self.player.is_alive and not self.game_over:
            self.game_over = True
            self.score_manager.save_score()
        
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
        
        title_text = "Game Over!"
        title_surface = self.font_large.render(title_text, True, self.colors['red'])
        title_rect = title_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 80))
        self.screen.blit(title_surface, title_rect)
        
        score_text = f"Final Score: {self.score_manager.current_score}"
        score_surface = self.font_medium.render(score_text, True, self.colors['yellow'])
        score_rect = score_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(score_surface, score_rect)
        
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
            
        if self.debug_keys and self.game_started:
            debug_text = "Keys: " + " ".join(self.debug_keys)
            text_surface = self.font_small.render(debug_text, True, self.colors['blue'])
            game_surface.blit(text_surface, (10, 10))
            
        for pack in self.health_packs:
            x = int(pack.position.x)
            y = int(pack.position.y)
            pygame.draw.circle(game_surface, self.colors['pink'], (x, y), pack.radius)
            pygame.draw.circle(game_surface, self.colors['red'], (x, y), pack.radius, 2)
            plus_text = self.font_small.render("+", True, self.colors['white'])
            plus_rect = plus_text.get_rect(center=(x, y))
            game_surface.blit(plus_text, plus_rect)
            
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
        
        self.draw_score_section(ui_surface, 60)
        self.draw_status_section(ui_surface, 160)
        self.draw_buttons(ui_surface)
        self.draw_controls(ui_surface, 400)
        self.draw_leaderboard(ui_surface, 500)
        
        self.screen.blit(ui_surface, (self.GAME_AREA_WIDTH, 0))
        
    def draw_score_section(self, surface, y_offset):
        """绘制分数区域"""
        section_title = self.font_medium.render("Score", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        score_text = f"Current: {self.score_manager.current_score}"
        score_surface = self.font_medium.render(score_text, True, self.colors['cyan'])
        surface.blit(score_surface, (20, y_offset + 30))
        
    def draw_status_section(self, surface, y_offset):
        """绘制状态信息区域"""
        section_title = self.font_medium.render("Status", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        y = y_offset + 30
        
        player_text = f"Player: {self.player.hp:.0f}/{self.player.max_hp:.0f}"
        player_color = self.colors['green'] if self.player.is_alive else self.colors['gray']
        surface.blit(self.font_small.render(player_text, True, player_color), (20, y))
        y += 22
        
        teammate_text = f"AI: {self.teammate.hp:.0f}/{self.teammate.max_hp:.0f}"
        teammate_color = self.colors['cyan'] if self.teammate.is_alive else self.colors['gray']
        surface.blit(self.font_small.render(teammate_text, True, teammate_color), (20, y))
        y += 22
        
        behavior_text = f"Action: {self.teammate.current_behavior}"
        surface.blit(self.font_small.render(behavior_text, True, self.colors['orange']), (20, y))
        y += 22
        
        potion_text = f"Potions: {self.teammate.healing_potion_count}"
        surface.blit(self.font_small.render(potion_text, True, self.colors['pink']), (20, y))
        y += 30
        
        enemy_count = sum(1 for e in self.enemies if e.is_alive)
        enemy_text = f"Enemies: {enemy_count}/{self.config.spawn.max_enemies}"
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
        
        y = y_offset + 30
        for key, action in controls:
            key_text = self.font_small.render(key, True, self.colors['cyan'])
            action_text = self.font_small.render(f"- {action}", True, self.colors['white'])
            surface.blit(key_text, (20, y))
            surface.blit(action_text, (140, y))
            y += 20
            
    def draw_leaderboard(self, surface, y_offset):
        """绘制排行榜"""
        title = self.font_medium.render("Top Scores", True, self.colors['yellow'])
        surface.blit(title, (20, y_offset))
        
        top_scores = self.score_manager.get_top_scores(5)
        y = y_offset + 30
        
        for i, entry in enumerate(top_scores):
            rank_text = f"{i+1}. {entry.score}"
            text_surface = self.font_small.render(rank_text, True, self.colors['white'])
            surface.blit(text_surface, (20, y))
            y += 18
            
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
    game = GameGUIEnhanced()
    game.run()
