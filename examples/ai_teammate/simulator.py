import time
from typing import List
from .entities import Player, Teammate, Enemy, Vector2
from .ai_behavior import AITeammate
from behavior_tree import Blackboard


class BattleSimulator:
    """战斗场景模拟器
    
    用于模拟和可视化AI队友的行为
    """
    
    def __init__(self):
        """初始化战斗模拟器"""
        self.frame_count = 0  # 帧计数
        self.player = Player(Vector2(0, 0))  # 玩家
        self.teammate = Teammate("AI队友", Vector2(2, 2))  # AI队友
        self.enemies: List[Enemy] = []  # 敌人列表
        self.blackboard = Blackboard()  # 黑板
        self.ai_teammate = AITeammate(self.teammate, self.player, self.blackboard)  # AI控制器
        self.logs: List[str] = []  # 日志列表

    def add_enemy(self, enemy: Enemy):
        """添加敌人到场景
        
        Args:
            enemy: 要添加的敌人
        """
        self.enemies.append(enemy)
        self.ai_teammate.add_enemy(enemy)

    def log(self, message: str):
        """记录日志
        
        Args:
            message: 日志消息
        """
        timestamp = f"[帧 {self.frame_count:03d}]"
        log_message = f"{timestamp} {message}"
        self.logs.append(log_message)
        print(log_message)

    def draw_scene(self):
        """绘制ASCII场景可视化"""
        width = 40
        height = 20
        grid = [[' ' for _ in range(width)] for _ in range(height)]

        def world_to_screen(pos: Vector2):
            """世界坐标转屏幕坐标"""
            x = int(pos.x + width // 2)
            y = int(height // 2 - pos.y)
            return max(0, min(width - 1, x)), max(0, min(height - 1, y))

        # 绘制玩家
        px, py = world_to_screen(self.player.position)
        if 0 <= px < width and 0 <= py < height:
            grid[py][px] = 'P'

        # 绘制AI队友
        tx, ty = world_to_screen(self.teammate.position)
        if 0 <= tx < width and 0 <= ty < height:
            grid[ty][tx] = 'T'

        # 绘制敌人
        for enemy in self.enemies:
            if enemy.is_alive:
                ex, ey = world_to_screen(enemy.position)
                if 0 <= ex < width and 0 <= ey < height:
                    grid[ey][ex] = 'E'

        # 输出场景
        print("\n" + "=" * width)
        for row in grid:
            print('|' + ''.join(row) + '|')
        print("=" * width)
        print("图例: P=玩家, T=AI队友, E=敌人")
        print(f"玩家: {self.player}")
        print(f"AI队友: {self.teammate} | 当前行为: {self.teammate.current_behavior} | 药水: {self.teammate.healing_potion_count}")
        for i, enemy in enumerate(self.enemies):
            status = "存活" if enemy.is_alive else "死亡"
            print(f"敌人{i+1}: {enemy} ({status})")

    def simulate_frame(self):
        """模拟一帧"""
        self.frame_count += 1
        self.log(f"--- 开始第 {self.frame_count} 帧 ---")

        # 更新AI队友
        self.ai_teammate.update()

        # 更新敌人（此处留空，可扩展）
        for enemy in self.enemies:
            if enemy.is_alive:
                pass

        # 绘制场景
        self.draw_scene()
        print()

    def run_scenario(self, num_frames: int = 30, delay: float = 0.5):
        """运行场景
        
        Args:
            num_frames: 帧数
            delay: 每帧延迟时间（秒）
        """
        print("=" * 60)
        print("AI队友行为树模拟")
        print("=" * 60)
        print()

        for _ in range(num_frames):
            self.simulate_frame()
            time.sleep(delay)

        print("\n" + "=" * 60)
        print("模拟结束!")
        print("=" * 60)

    def scenario_1_basic_combat(self):
        """场景1: 基础战斗场景
        
        单个敌人，演示AI的战斗行为
        """
        print("\n场景1: 基础战斗场景")
        print("-" * 60)
        
        enemy1 = Enemy("哥布林", Vector2(5, 3))
        self.add_enemy(enemy1)
        
        self.run_scenario(num_frames=20)

    def scenario_2_emergency_heal(self):
        """场景2: 紧急治疗场景
        
        AI队友血量低，演示紧急治疗行为
        """
        print("\n场景2: 紧急治疗场景")
        print("-" * 60)
        
        enemy1 = Enemy("哥布林", Vector2(5, 3))
        self.add_enemy(enemy1)
        
        self.teammate.take_damage(75)
        self.log(f"AI队友受到伤害，血量降至 {self.teammate.hp}")
        
        self.run_scenario(num_frames=15)

    def scenario_3_multiple_enemies(self):
        """场景3: 多个敌人场景
        
        多个敌人，演示AI的战斗选择
        """
        print("\n场景3: 多个敌人场景")
        print("-" * 60)
        
        enemy1 = Enemy("哥布林", Vector2(5, 3))
        enemy2 = Enemy("骷髅", Vector2(-4, -4))
        self.add_enemy(enemy1)
        self.add_enemy(enemy2)
        
        self.run_scenario(num_frames=25)
