
import sys
import os
import math
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

import pygame
from typing import Dict, Tuple, Optional
from .config import GameConfig
from .entities import Vector2, NPC, Enemy, Character, Behavior


class GameGUI:
    """AI行为研究可视化界面"""
    
    def __init__(self, config: Optional[GameConfig] = None):
        """初始化GUI"""
        pygame.init()
        
        self.config = config if config else GameConfig()
        
        self.WINDOW_WIDTH = 1200
        self.WINDOW_HEIGHT = 700
        self.GAME_AREA_WIDTH = int(self.config.map.map_width)
        self.GAME_AREA_HEIGHT = int(self.config.map.map_height)
        self.UI_WIDTH = self.WINDOW_WIDTH - self.GAME_AREA_WIDTH
        self.UI_HEIGHT = self.WINDOW_HEIGHT
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("AI Behavior Research - FSM vs BehaviorTree vs Utility AI")
        
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
            'dark_red': (200, 0, 0),
            'green': (0, 255, 0),
            'dark_green': (0, 200, 0),
            'blue': (0, 0, 255),
            'dark_blue': (0, 0, 200),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'cyan': (0, 255, 255),
            'pink': (255, 192, 203),
            'purple': (128, 0, 128),
            'gold': (255, 215, 0),
            'teal': (0, 128, 128)
        }
        
        self.npc_colors = {
            'fsm': {'body': self.colors['red'], 'outline': self.colors['dark_red']},
            'bt': {'body': self.colors['blue'], 'outline': self.colors['dark_blue']},
            'utility': {'body': self.colors['green'], 'outline': self.colors['dark_green']}
        }
        
        self.decision_type_names = {
            'fsm': 'FSM',
            'bt': 'Behavior Tree',
            'utility': 'Utility AI'
        }
        
        self.load_fonts()
    
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
                        self.font_large = pygame.font.Font(font_path, 22)
                        self.font_medium = pygame.font.Font(font_path, 16)
                        self.font_small = pygame.font.Font(font_path, 12)
                        break
                    except:
                        continue
            except:
                continue
        
        if self.font_large is None:
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)
    
    def handle_events(self) -> bool:
        """处理输入事件，返回是否应该继续运行"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_paused = not self.game_paused
                elif event.key == pygame.K_r:
                    self.game_paused = False
        
        return self.running
    
    def render(self, game_state):
        """
        渲染游戏
        
        Args:
            game_state: 游戏状态对象，包含 npcs, enemies, grid, frame_count, player_position 等属性
        """
        self.screen.fill(self.colors['dark_gray'])
        
        self.draw_game_area(game_state)
        self.draw_ui_panel(game_state)
        
        pygame.display.flip()
        self.clock.tick(self.FPS)
    
    def draw_game_area(self, game_state):
        """绘制游戏区域（地图）"""
        game_surface = pygame.Surface((self.GAME_AREA_WIDTH, self.GAME_AREA_HEIGHT))
        game_surface.fill(self.colors['light_gray'])
        
        self.draw_grid(game_surface)
        self.draw_obstacles(game_surface, game_state.grid)
        
        for enemy in game_state.enemies:
            if enemy.is_alive:
                self.draw_character(game_surface, enemy, self.colors['purple'], self.colors['black'])
            else:
                self.draw_dead_character(game_surface, enemy, self.colors['purple'])
        
        for npc in game_state.npcs:
            if npc.is_alive:
                colors = self.npc_colors.get(npc.decision_type, {'body': self.colors['gray'], 'outline': self.colors['dark_gray']})
                self.draw_npc(game_surface, npc, colors['body'], colors['outline'])
            else:
                colors = self.npc_colors.get(npc.decision_type, {'body': self.colors['gray'], 'outline': self.colors['dark_gray']})
                self.draw_dead_character(game_surface, npc, colors['body'])
        
        self.screen.blit(game_surface, (0, 0))
    
    def draw_grid(self, surface):
        """绘制网格"""
        grid_size = int(self.config.map.grid_size)
        
        for x in range(0, self.GAME_AREA_WIDTH, grid_size):
            pygame.draw.line(surface, self.colors['gray'], (x, 0), (x, self.GAME_AREA_HEIGHT))
        for y in range(0, self.GAME_AREA_HEIGHT, grid_size):
            pygame.draw.line(surface, self.colors['gray'], (0, y), (self.GAME_AREA_WIDTH, y))
    
    def draw_obstacles(self, surface, grid):
        """绘制障碍物"""
        grid_size = int(self.config.map.grid_size)
        
        for (grid_x, grid_y) in grid.obstacles:
            rect_x = grid_x * grid_size
            rect_y = grid_y * grid_size
            pygame.draw.rect(surface, self.colors['dark_gray'], (rect_x, rect_y, grid_size, grid_size))
    
    def draw_npc(self, surface, npc: NPC, body_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """绘制NPC（带状态信息）"""
        x = int(npc.position.x)
        y = int(npc.position.y)
        radius = 20
        
        pygame.draw.circle(surface, body_color, (x, y), radius)
        pygame.draw.circle(surface, outline_color, (x, y), radius, 3)
        
        eye_offset = 6
        eye_radius = 3
        angle = npc.rotation
        eye1_x = x + int(math.cos(angle) * eye_offset - math.sin(angle) * 4)
        eye1_y = y + int(math.sin(angle) * eye_offset + math.cos(angle) * 4)
        eye2_x = x + int(math.cos(angle) * eye_offset + math.sin(angle) * 4)
        eye2_y = y + int(math.sin(angle) * eye_offset - math.cos(angle) * 4)
        
        pygame.draw.circle(surface, self.colors['white'], (eye1_x, eye1_y), eye_radius)
        pygame.draw.circle(surface, self.colors['white'], (eye2_x, eye2_y), eye_radius)
        pygame.draw.circle(surface, self.colors['black'], (eye1_x, eye1_y), 1)
        pygame.draw.circle(surface, self.colors['black'], (eye2_x, eye2_y), 1)
        
        self.draw_health_bar(surface, npc, x, y - radius - 12)
        self.draw_npc_info(surface, npc, x, y - radius - 28)
    
    def draw_character(self, surface, character: Character, body_color: Tuple[int, int, int], outline_color: Tuple[int, int, int]):
        """绘制角色"""
        x = int(character.position.x)
        y = int(character.position.y)
        radius = 18
        
        pygame.draw.circle(surface, body_color, (x, y), radius)
        pygame.draw.circle(surface, outline_color, (x, y), radius, 2)
        
        self.draw_health_bar(surface, character, x, y - radius - 10)
        self.draw_name(surface, character, x, y - radius - 24)
    
    def draw_dead_character(self, surface, character: Character, color: Tuple[int, int, int]):
        """绘制死亡角色"""
        x = int(character.position.x)
        y = int(character.position.y)
        radius = 18
        
        pygame.draw.circle(surface, self.colors['gray'], (x, y), radius)
        pygame.draw.line(surface, color, (x - 8, y - 8), (x + 8, y + 8), 3)
        pygame.draw.line(surface, color, (x + 8, y - 8), (x - 8, y + 8), 3)
    
    def draw_health_bar(self, surface, character: Character, x: int, y: int):
        """绘制血条"""
        bar_width = 40
        bar_height = 6
        fill_width = int(bar_width * character.hp_percentage())
        
        pygame.draw.rect(surface, self.colors['black'], (x - bar_width // 2 - 1, y - 1, bar_width + 2, bar_height + 2))
        pygame.draw.rect(surface, self.colors['dark_red'], (x - bar_width // 2, y, bar_width, bar_height))
        pygame.draw.rect(surface, self.colors['green'], (x - bar_width // 2, y, fill_width, bar_height))
    
    def draw_npc_info(self, surface, npc: NPC, x: int, y: int):
        """绘制NPC信息（行为和决策方式）"""
        behavior_text = npc.current_behavior.value if hasattr(npc, 'current_behavior') else "Unknown"
        decision_type = self.decision_type_names.get(npc.decision_type, npc.decision_type)
        
        info_text = f"{decision_type} - {behavior_text}"
        text_surface = self.font_small.render(info_text, True, self.colors['black'])
        text_rect = text_surface.get_rect(center=(x, y))
        surface.blit(text_surface, text_rect)
    
    def draw_name(self, surface, character: Character, x: int, y: int):
        """绘制角色名称"""
        text = self.font_small.render(character.name, True, self.colors['black'])
        text_rect = text.get_rect(center=(x, y))
        surface.blit(text, text_rect)
    
    def draw_ui_panel(self, game_state):
        """绘制UI面板"""
        ui_surface = pygame.Surface((self.UI_WIDTH, self.UI_HEIGHT))
        ui_surface.fill(self.colors['black'])
        
        title = self.font_large.render("AI Behavior Research", True, self.colors['white'])
        ui_surface.blit(title, (20, 20))
        
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.font_medium.render(fps_text, True, self.colors['cyan'])
        ui_surface.blit(fps_surface, (20, 55))
        
        frame_text = f"Frame: {game_state.frame_count}"
        frame_surface = self.font_medium.render(frame_text, True, self.colors['orange'])
        ui_surface.blit(frame_surface, (20, 80))
        
        if self.game_paused:
            pause_text = "PAUSED - Press SPACE to resume"
            pause_surface = self.font_medium.render(pause_text, True, self.colors['yellow'])
            ui_surface.blit(pause_surface, (20, 105))
        
        self.draw_npc_stats(ui_surface, game_state.npcs, 140)
        self.draw_enemy_stats(ui_surface, game_state.enemies, 350)
        self.draw_controls(ui_surface, 550)
        self.draw_legend(ui_surface, 620)
        
        self.screen.blit(ui_surface, (self.GAME_AREA_WIDTH, 0))
    
    def draw_npc_stats(self, surface, npcs, y_offset):
        """绘制NPC统计信息"""
        section_title = self.font_medium.render("NPC Status", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        y = y_offset + 30
        for i, npc in enumerate(npcs):
            colors = self.npc_colors.get(npc.decision_type, {'body': self.colors['gray'], 'outline': self.colors['dark_gray']})
            decision_name = self.decision_type_names.get(npc.decision_type, npc.decision_type)
            
            status_text = "ALIVE" if npc.is_alive else "DEAD"
            status_color = self.colors['green'] if npc.is_alive else self.colors['red']
            
            pygame.draw.rect(surface, colors['body'], (20, y, 12, 12))
            
            name_text = self.font_small.render(f"{npc.name} ({decision_name})", True, self.colors['white'])
            surface.blit(name_text, (40, y))
            
            hp_text = self.font_small.render(f"HP: {npc.hp:.0f}/{npc.max_hp:.0f}", True, self.colors['light_gray'])
            surface.blit(hp_text, (40, y + 15))
            
            behavior = npc.current_behavior.value if hasattr(npc, 'current_behavior') else "Unknown"
            behavior_text = self.font_small.render(f"Action: {behavior}", True, self.colors['orange'])
            surface.blit(behavior_text, (40, y + 30))
            
            status_surface = self.font_small.render(status_text, True, status_color)
            surface.blit(status_surface, (40, y + 45))
            
            y += 65
    
    def draw_enemy_stats(self, surface, enemies, y_offset):
        """绘制敌人统计信息"""
        section_title = self.font_medium.render("Enemy Status", True, self.colors['yellow'])
        surface.blit(section_title, (20, y_offset))
        
        alive_count = sum(1 for e in enemies if e.is_alive)
        count_text = f"Alive: {alive_count}/{len(enemies)}"
        count_surface = self.font_medium.render(count_text, True, self.colors['purple'])
        surface.blit(count_surface, (20, y_offset + 30))
    
    def draw_controls(self, surface, y_offset):
        """绘制操作说明"""
        title = self.font_medium.render("Controls", True, self.colors['yellow'])
        surface.blit(title, (20, y_offset))
        
        controls = [
            ("SPACE", "Pause/Resume"),
            ("R", "Reset Pause"),
        ]
        
        y = y_offset + 25
        for key, action in controls:
            key_text = self.font_small.render(key, True, self.colors['cyan'])
            action_text = self.font_small.render(f"- {action}", True, self.colors['white'])
            surface.blit(key_text, (20, y))
            surface.blit(action_text, (90, y))
            y += 18
    
    def draw_legend(self, surface, y_offset):
        """绘制图例"""
        title = self.font_medium.render("Legend", True, self.colors['yellow'])
        surface.blit(title, (20, y_offset))
        
        legends = [
            (self.colors['red'], "FSM NPC"),
            (self.colors['blue'], "Behavior Tree NPC"),
            (self.colors['green'], "Utility AI NPC"),
            (self.colors['purple'], "Enemy"),
        ]
        
        y = y_offset + 25
        for color, label in legends:
            pygame.draw.rect(surface, color, (20, y, 15, 15))
            label_text = self.font_small.render(label, True, self.colors['white'])
            surface.blit(label_text, (45, y))
            y += 20
    
    def quit(self):
        """退出GUI"""
        pygame.quit()

