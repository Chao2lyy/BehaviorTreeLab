import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pygame
from ai_teammate.config import GameConfig
from ai_teammate.score_manager import ScoreManager
from ai_teammate.game_logic import GameLogic
from ai_teammate.advanced_enemies import EnemyType
from ai_teammate.entities import Vector2


class GameGUI:
    """AI队友行为树图形化游戏界面 - 重构最终版"""
    
    def __init__(self):
        """初始化游戏"""
        pygame.init()
        
        self.config = GameConfig()
        self.score_manager = ScoreManager(self.config)
        
        self.WINDOW_WIDTH = 1300
        self.WINDOW_HEIGHT = 700
        self.GAME_AREA_WIDTH = 750
        self.GAME_AREA_HEIGHT = 700
        self.UI_WIDTH = 550
        self.UI_HEIGHT = 700
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("AI Teammate - Refactored Final Version")
        
        self.clock = pygame.time.Clock()
        self.FPS = 60
        
        self.running = True
        self.game_paused = False
        
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
            'purple': (128, 0, 128),
            'gold': (255, 215, 0),
            'teal': (0, 128, 128)
        }
        
        self.load_fonts()
        self.game_logic = GameLogic(self.config, self.score_manager, self.GAME_AREA_WIDTH, self.GAME_AREA_HEIGHT)
    
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
                        self.font_large = pygame.font.Font(font_path, 24)
                        self.font_medium = pygame.font.Font(font_path, 18)
                        self.font_small = pygame.font.Font(font_path, 14)
                        break
                    except:
                        continue
            except:
                continue
        
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)
    
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
        if self.game_paused or not self.game_logic.player.is_alive or self.game_logic.game_over or not self.game_logic.game_started:
            return
            
        dx, dy = 0, 0
        
        if keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_s]:
            dy = 1
        if keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP]:
            dy = -1
        if keys[pygame.K_DOWN]:
            dy = 1
        if keys[pygame.K_LEFT]:
            dx = -1
        if keys[pygame.K_RIGHT]:
            dx = 1
        
        if dx != 0 or dy != 0:
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
            new_x = self.game_logic.player.position.x + dx * self.game_logic.player_speed
            new_y = self.game_logic.player.position.y + dy * self.game_logic.player_speed
            
            new_x = max(30, min(self.GAME_AREA_WIDTH - 30, new_x))
            new_y = max(30, min(self.GAME_AREA_HEIGHT - 30, new_y))
            
            self.game_logic.player.position = Vector2(new_x, new_y)
            
            if dx != 0 or dy != 0:
                self.game_logic.player.look_at(Vector2(new_x + dx, new_y + dy))
    
    def handle_mouse_click(self, pos):
        """处理鼠标点击"""
        x, y = pos
        if x > self.GAME_AREA_WIDTH:
            ui_x = x - self.GAME_AREA_WIDTH
            ui_y = y
            
            if not self.game_logic.game_started and 50 <= ui_x <= 200 and 260 <= ui_y <= 300:
                self.game_logic.start_game()
            elif self.game_logic.game_started and 20 <= ui_x <= 120 and 260 <= ui_y <= 300:
                self.toggle_pause()
            elif self.game_logic.game_started and 130 <= ui_x <= 230 and 260 <= ui_y <= 300:
                self.game_logic = GameLogic(self.config, self.score_manager, self.GAME_AREA_WIDTH, self.GAME_AREA_HEIGHT)
                self.game_paused = False
    
    def toggle_pause(self):
        """暂停/继续游戏"""
        self.game_paused = not self.game_paused
    
    def update(self):
        """更新游戏状态"""
        if not self.game_paused:
            self.game_logic.update()
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(self.colors['dark_gray'])
        
        self.draw_game_area()
        self.draw_ui_panel()
        
        if self.game_logic.game_over:
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
        
        level_text = f"Final Level: {self.game_logic.player_level.level}"
        level_surface = self.font_medium.render(level_text, True, self.colors['cyan'])
        level_rect = level_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(level_surface, level_rect)
        
        phase_text = f"Reached Phase: {self.game_logic.difficulty_phase}"
        phase_surface = self.font_medium.render(phase_text, True, self.colors['orange'])
        phase_rect = phase_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(phase_surface, phase_rect)
        
        restart_text = "Press Restart to play again"
        restart_surface = self.font_medium.render(restart_text, True, self.colors['white'])
        restart_rect = restart_surface.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 110))
        self.screen.blit(restart_surface, restart_rect)
    
    def draw_game_area(self):
        """绘制游戏区域"""
        game_surface = pygame.Surface((self.GAME_AREA_WIDTH, self.GAME_AREA_HEIGHT))
        game_surface.fill(self.colors['light_gray'])
        
        for x in range(0, self.GAME_AREA_WIDTH, 50):
            pygame.draw.line(game_surface, self.colors['gray'], (x, 0), (x, self.GAME_AREA_HEIGHT))
        for y in range(0, self.GAME_AREA_HEIGHT, 50):
            pygame.draw.line(game_surface, self.colors['gray'], (0, y), (self.GAME_AREA_WIDTH, y))
        
        for pack in self.game_logic.health_packs:
            x = int(pack.position.x)
            y = int(pack.position.y)
            pygame.draw.circle(game_surface, self.colors['pink'], (x, y), pack.radius)
            pygame.draw.circle(game_surface, self.colors['red'], (x, y), pack.radius, 2)
            plus_text = self.font_small.render("+", True, self.colors['white'])
            plus_rect = plus_text.get_rect(center=(x, y))
            game_surface.blit(plus_text, plus_rect)
        
        for pack in self.game_logic.skill_packs:
            x = int(pack.position.x)
            y = int(pack.position.y)
            color = self.colors['gold'] if pack.skill_type == 'bullet' else self.colors['purple']
            pygame.draw.circle(game_surface, color, (x, y), pack.radius)
            pygame.draw.circle(game_surface, self.colors['white'], (x, y), pack.radius, 2)
            skill_text = self.font_small.render("S", True, self.colors['white'])
            skill_rect = skill_text.get_rect(center=(x, y))
            game_surface.blit(skill_text, skill_rect)
        
        for proj in self.game_logic.projectiles:
            x = int(proj.position.x)
            y = int(proj.position.y)
            color = self.colors['cyan'] if proj.team == 'friendly' else self.colors['orange']
            pygame.draw.circle(game_surface, color, (x, y), proj.radius)
        
        for dart_pos, _ in getattr(self.game_logic.player_skills.get('dart'), 'darts', []):
            x = int(dart_pos.x)
            y = int(dart_pos.y)
            pygame.draw.circle(game_surface, self.colors['gold'], (x, y), 12)
            pygame.draw.circle(game_surface, self.colors['yellow'], (x, y), 12, 2)
        
        for dart_pos, _ in getattr(self.game_logic.teammate_skills.get('dart'), 'darts', []):
            x = int(dart_pos.x)
            y = int(dart_pos.y)
            pygame.draw.circle(game_surface, self.colors['teal'], (x, y), 12)
            pygame.draw.circle(game_surface, self.colors['cyan'], (x, y), 12, 2)
        
        enemy_colors = {
            EnemyType.WARRIOR: self.colors['red'],
            EnemyType.MAGE: self.colors['purple'],
            EnemyType.GUNNER: self.colors['orange'],
            EnemyType.GENERAL: self.colors['gold'],
            EnemyType.COMMANDER: self.colors['dark_gray']
        }
        
        for enemy in self.game_logic.enemies:
            if enemy.is_alive:
                color = enemy_colors.get(enemy.enemy_type, self.colors['red'])
                self.draw_character(game_surface, enemy, color, self.colors['black'])
            else:
                color = enemy_colors.get(enemy.enemy_type, self.colors['red'])
                self.draw_dead_character(game_surface, enemy, color)
        
        if self.game_logic.teammate.is_alive:
            self.draw_character(game_surface, self.game_logic.teammate, self.colors['cyan'], self.colors['blue'])
        else:
            self.draw_dead_character(game_surface, self.game_logic.teammate, self.colors['cyan'])
        
        if self.game_logic.player.is_alive:
            self.draw_character(game_surface, self.game_logic.player, self.colors['green'], self.colors['dark_gray'])
        else:
            self.draw_dead_character(game_surface, self.game_logic.player, self.colors['green'])
        
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
        
        title = self.font_large.render("BehaviorTreeLab", True, self.colors['white'])
        ui_surface.blit(title, (30, 20))
        
        self.draw_score_section(ui_surface, 60)
        self.draw_level_section(ui_surface, 130)
        self.draw_skill_section(ui_surface, 210)
        self.draw_status_section(ui_surface, 310)
        self.draw_buttons(ui_surface)
        self.draw_controls(ui_surface, 480)
        self.draw_leaderboard(ui_surface, 580)
        
        self.screen.blit(ui_surface, (self.GAME_AREA_WIDTH, 0))
    
    def draw_score_section(self, surface, y_offset):
        """绘制分数区域"""
        section_title = self.font_medium.render("Score & Phase", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        score_text = f"Score: {self.score_manager.current_score}"
        score_surface = self.font_medium.render(score_text, True, self.colors['cyan'])
        surface.blit(score_surface, (20, y_offset + 25))
        
        phase_text = f"Phase: {self.game_logic.difficulty_phase}"
        phase_surface = self.font_medium.render(phase_text, True, self.colors['orange'])
        surface.blit(phase_surface, (20, y_offset + 48))
    
    def draw_level_section(self, surface, y_offset):
        """绘制等级区域"""
        section_title = self.font_medium.render("Level System", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        level_text = f"Player Level: {self.game_logic.player_level.level}"
        level_surface = self.font_medium.render(level_text, True, self.colors['green'])
        surface.blit(level_surface, (20, y_offset + 25))
        
        exp_text = f"EXP: {self.game_logic.player_level.experience}/{self.game_logic.player_level.experience_to_next}"
        exp_surface = self.font_small.render(exp_text, True, self.colors['light_gray'])
        surface.blit(exp_surface, (20, y_offset + 45))
    
    def draw_skill_section(self, surface, y_offset):
        """绘制技能区域"""
        section_title = self.font_medium.render("Skills", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        y = y_offset + 25
        for skill_name, skill in self.game_logic.player_skills.items():
            if skill_name == 'bullet':
                text = f"Bullet Lv.{skill.level} (Rate:{skill.fire_rate})"
                color = self.colors['cyan']
            else:
                text = f"Dart Lv.{skill.level} (x{skill.dart_count})"
                color = self.colors['purple']
            text_surface = self.font_small.render(text, True, color)
            surface.blit(text_surface, (20, y))
            y += 20
    
    def draw_status_section(self, surface, y_offset):
        """绘制状态信息区域"""
        section_title = self.font_medium.render("Status", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        y = y_offset + 25
        
        player_text = f"Player: {self.game_logic.player.hp:.0f}/{self.game_logic.player.max_hp:.0f}"
        player_color = self.colors['green'] if self.game_logic.player.is_alive else self.colors['gray']
        surface.blit(self.font_small.render(player_text, True, player_color), (20, y))
        y += 18
        
        teammate_text = f"AI: {self.game_logic.teammate.hp:.0f}/{self.game_logic.teammate.max_hp:.0f}"
        teammate_color = self.colors['cyan'] if self.game_logic.teammate.is_alive else self.colors['gray']
        surface.blit(self.font_small.render(teammate_text, True, teammate_color), (20, y))
        y += 18
        
        behavior_text = f"Action: {self.game_logic.teammate.current_behavior}"
        surface.blit(self.font_small.render(behavior_text, True, self.colors['orange']), (20, y))
        y += 18
        
        potion_text = f"Potions: {self.game_logic.teammate.healing_potion_count}"
        surface.blit(self.font_small.render(potion_text, True, self.colors['pink']), (20, y))
        y += 25
        
        enemy_count = sum(1 for e in self.game_logic.enemies if e.is_alive)
        enemy_text = f"Enemies: {enemy_count}"
        surface.blit(self.font_small.render(enemy_text, True, self.colors['red']), (20, y))
    
    def draw_buttons(self, surface):
        """绘制控制按钮"""
        if not self.game_logic.game_started:
            self.draw_button(surface, "Start Game", 50, 260, 150, 40, self.colors['green'])
        else:
            pause_text = "Resume" if self.game_paused else "Pause"
            pause_color = self.colors['orange'] if self.game_paused else self.colors['yellow']
            self.draw_button(surface, pause_text, 20, 260, 100, 40, pause_color)
            self.draw_button(surface, "Restart", 130, 260, 100, 40, self.colors['blue'])
    
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
        ]
        
        y = y_offset + 25
        for key, action in controls:
            key_text = self.font_small.render(key, True, self.colors['cyan'])
            action_text = self.font_small.render(f"- {action}", True, self.colors['white'])
            surface.blit(key_text, (20, y))
            surface.blit(action_text, (140, y))
            y += 18
    
    def draw_leaderboard(self, surface, y_offset):
        """绘制排行榜"""
        title = self.font_medium.render("Top Scores", True, self.colors['yellow'])
        surface.blit(title, (20, y_offset))
        
        top_scores = self.score_manager.get_top_scores(5)
        y = y_offset + 25
        
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
    game = GameGUI()
    game.run()
