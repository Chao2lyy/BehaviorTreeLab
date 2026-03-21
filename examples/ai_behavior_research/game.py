import random
from typing import List, Dict, Optional
from dataclasses import dataclass

from .config import GameConfig
from .entities import Vector2, NPC, Enemy, Character, Behavior
from .grid_map import Grid
from .pathfinding import find_path
from .movement import SteeringController
from .combat import CombatSystem
from .fsm_npc import FSMNPC, WorldState as FSMWorldState
from .bt_npc import BTNPC, WorldState as BTWorldState
from .utility_ai import UtilityAI, WorldState as UtilityWorldState
from .gui import GameGUI


@dataclass
class WorldState:
    """统一的世界状态类，用于收集游戏世界信息"""
    
    my_health: float = 1.0
    """自身血量（归一化到0-1）"""
    
    enemy_distance: float = 1.0
    """到最近敌人的距离（归一化到0-1）"""
    
    enemy_threat: float = 0.0
    """敌人威胁（归一化到0-1）"""
    
    enemy_count: int = 0
    """敌人数量"""
    
    in_safe_area: bool = True
    """是否在安全区域"""
    
    heal_available: bool = True
    """治疗是否可用"""
    
    ammo_level: float = 1.0
    """弹药量（归一化到0-1）"""
    
    safe_area: float = 1.0
    """安全区域（归一化到0-1）"""
    
    distance_to_guard_point: float = 1.0
    """到警戒点的距离（归一化到0-1）"""
    
    guard_point: Optional[Vector2] = None
    """警戒点位置"""


class NPCController:
    """NPC控制器，整合所有决策系统"""
    
    def __init__(self, npc: NPC, config: GameConfig):
        self.npc = npc
        self.config = config
        self.fsm_npc = FSMNPC(config.npc)
        self.bt_npc = BTNPC(config.npc)
        self.utility_ai = UtilityAI(config.utility_weights)
        self.steering_controller = SteeringController(config)
        self.steering_controller.attach_to_character(npc)
        self.current_path: List[Vector2] = []
        self.guard_position = npc.position
    
    def make_decision(self, world_state: WorldState) -> Behavior:
        """根据decision_type选择决策系统并做出决策"""
        if self.npc.decision_type == 'fsm':
            return self._make_fsm_decision(world_state)
        elif self.npc.decision_type == 'bt':
            return self._make_bt_decision(world_state)
        elif self.npc.decision_type == 'utility':
            return self._make_utility_decision(world_state)
        else:
            return Behavior.Guard
    
    def _make_fsm_decision(self, world_state: WorldState) -> Behavior:
        """使用FSM决策"""
        fsm_state = FSMWorldState(
            my_health=world_state.my_health,
            enemy_distance=world_state.enemy_distance,
            enemy_threat=world_state.enemy_threat,
            enemy_count=world_state.enemy_count,
            in_safe_area=world_state.in_safe_area,
            heal_available=world_state.heal_available
        )
        action_desc = self.fsm_npc.update(fsm_state)
        current_fsm_state = self.fsm_npc.get_current_state()
        state_to_behavior = {
            'Idle': Behavior.Guard,
            'Attack': Behavior.Attack,
            'Flee': Behavior.Flee,
            'Heal': Behavior.Heal
        }
        return state_to_behavior.get(current_fsm_state.value, Behavior.Guard)
    
    def _make_bt_decision(self, world_state: WorldState) -> Behavior:
        """使用行为树决策"""
        bt_state = BTWorldState(
            my_health=world_state.my_health,
            enemy_distance=world_state.enemy_distance,
            enemy_threat=world_state.enemy_threat,
            enemy_count=world_state.enemy_count,
            in_safe_area=world_state.in_safe_area,
            heal_available=world_state.heal_available
        )
        return self.bt_npc.tick(bt_state)
    
    def _make_utility_decision(self, world_state: WorldState) -> Behavior:
        """使用Utility AI决策"""
        utility_state = UtilityWorldState(
            my_health=world_state.my_health,
            enemy_threat=world_state.enemy_threat,
            enemy_count=float(world_state.enemy_count) / 5.0,
            ammo_level=world_state.ammo_level,
            safe_area=world_state.safe_area,
            distance_to_guard_point=world_state.distance_to_guard_point,
            guard_point=world_state.guard_point
        )
        return self.utility_ai.decide(utility_state)


class Game:
    """游戏主类，管理游戏循环和所有实体"""
    
    def __init__(self, config: Optional[GameConfig] = None, use_gui: bool = True):
        self.config = config if config else GameConfig()
        self.grid = Grid(self.config.map)
        self.grid.create_sample_obstacles()
        self.combat_system = CombatSystem(self.config)
        
        self.npcs: List[NPC] = []
        self.npc_controllers: Dict[NPC, NPCController] = {}
        self.enemies: List[Enemy] = []
        
        self.frame_count = 0
        self.spawn_interval = 300
        self.max_enemies = 10
        self.is_running = False
        
        self.use_gui = use_gui
        self.gui = None
        if self.use_gui:
            self.gui = GameGUI(self.config)
        
        self._init_npcs()
    
    def _init_npcs(self):
        """初始化3个不同决策类型的NPC"""
        npc_types = [
            ('FSM_NPC', 'fsm', Vector2(150, 100)),
            ('BT_NPC', 'bt', Vector2(400, 100)),
            ('Utility_NPC', 'utility', Vector2(650, 100))
        ]
        
        for name, decision_type, position in npc_types:
            grid_x, grid_y = self.grid.world_to_grid(position)
            if not self.grid.is_walkable(grid_x, grid_y):
                position = Vector2(
                    position.x + 64,
                    position.y + 64
                )
            npc = NPC(name, position, self.config.npc.max_hp, decision_type)
            npc.guard_position = position
            self.npcs.append(npc)
            controller = NPCController(npc, self.config)
            self.npc_controllers[npc] = controller
    

    
    def _update_with_obstacle_avoidance(self, npc: NPC, controller, steering):
        """带障碍物避开的移动更新
        
        Args:
            npc: NPC实体
            controller: 移动控制器
            steering: 转向加速度
        """
        grid_size = self.config.map.grid_size
        
        test_positions = [
            npc.position + Vector2(steering.linear.x, steering.linear.y),
            npc.position + Vector2(steering.linear.x * 0.5, 0),
            npc.position + Vector2(0, steering.linear.y * 0.5),
            npc.position + Vector2(-steering.linear.y * 0.3, steering.linear.x * 0.3),
            npc.position + Vector2(steering.linear.y * 0.3, -steering.linear.x * 0.3),
        ]
        
        for test_pos in test_positions:
            grid_x, grid_y = self.grid.world_to_grid(test_pos)
            if self.grid.is_walkable(grid_x, grid_y):
                direction = test_pos - npc.position
                if direction.x != 0 or direction.y != 0:
                    normalized = direction.normalized()
                    new_steering = controller.steering_controller.behaviors.seek(
                        npc.position,
                        controller.steering_controller.velocity,
                        npc.position + normalized * grid_size,
                        controller.steering_controller.max_speed,
                        controller.steering_controller.max_acceleration
                    )
                    controller.steering_controller.update(
                        npc,
                        new_steering,
                        self.config.map.map_width,
                        self.config.map.map_height
                    )
                    return
        
        controller.steering_controller.stop()
    
    def spawn_enemy(self):
        """在地图边界随机生成敌人"""
        if len(self.enemies) >= self.max_enemies:
            return
        
        spawn_zone = self.config.map
        side = random.randint(0, 3)
        
        if side == 0:
            x = random.uniform(spawn_zone.spawn_zone_min_x, spawn_zone.spawn_zone_max_x)
            y = spawn_zone.spawn_zone_min_y
        elif side == 1:
            x = random.uniform(spawn_zone.spawn_zone_min_x, spawn_zone.spawn_zone_max_x)
            y = spawn_zone.spawn_zone_max_y
        elif side == 2:
            x = spawn_zone.spawn_zone_min_x
            y = random.uniform(spawn_zone.spawn_zone_min_y, spawn_zone.spawn_zone_max_y)
        else:
            x = spawn_zone.spawn_zone_max_x
            y = random.uniform(spawn_zone.spawn_zone_min_y, spawn_zone.spawn_zone_max_y)
        
        enemy_name = f"Enemy_{len(self.enemies)}"
        enemy = Enemy(enemy_name, Vector2(x, y), self.config.enemy.max_hp)
        self.enemies.append(enemy)
    
    def collect_world_state(self, npc: NPC) -> WorldState:
        """为NPC收集世界状态"""
        my_health = npc.hp_percentage()
        
        nearest_enemy = None
        min_distance = float('inf')
        for enemy in self.enemies:
            if enemy.is_alive:
                dist = npc.position.distance_to(enemy.position)
                if dist < min_distance:
                    min_distance = dist
                    nearest_enemy = enemy
        
        enemy_distance = min(min_distance / 500.0, 1.0) if nearest_enemy else 1.0
        enemy_threat = (1.0 - enemy_distance) if nearest_enemy else 0.0
        enemy_count = sum(1 for e in self.enemies if e.is_alive)
        
        center = Vector2(self.config.map.map_width / 2, self.config.map.map_height / 2)
        dist_to_center = npc.position.distance_to(center)
        in_safe_area = dist_to_center < 200.0
        safe_area = max(0.0, 1.0 - dist_to_center / 400.0)
        
        heal_available = npc.heal_cooldown_remaining <= 0
        ammo_level = 1.0
        
        distance_to_guard_point = 1.0
        guard_point = npc.guard_position
        if guard_point:
            distance_to_guard_point = min(npc.position.distance_to(guard_point) / 500.0, 1.0)
        
        return WorldState(
            my_health=my_health,
            enemy_distance=enemy_distance,
            enemy_threat=enemy_threat,
            enemy_count=enemy_count,
            in_safe_area=in_safe_area,
            heal_available=heal_available,
            ammo_level=ammo_level,
            safe_area=safe_area,
            distance_to_guard_point=distance_to_guard_point,
            guard_point=guard_point
        )
    
    def _safe_update_position(self, npc: NPC, controller, steering, target_pos):
        """安全地更新位置，确保不会进入障碍物
        
        Args:
            npc: NPC实体
            controller: 移动控制器
            steering: 转向加速度
            target_pos: 目标位置（用于备用避开策略）
        """
        grid_size = self.config.map.grid_size
        
        old_position = Vector2(npc.position.x, npc.position.y)
        
        controller.steering_controller.update(
            npc, steering, 
            self.config.map.map_width, 
            self.config.map.map_height
        )
        
        new_grid = self.grid.world_to_grid(npc.position)
        if not self.grid.is_walkable(new_grid[0], new_grid[1]):
            npc.position = old_position
            controller.steering_controller.last_safe_position = old_position
            controller.steering_controller.velocity = Vector2(0, 0)
            
            if target_pos:
                steering = controller.steering_controller.seek(npc.position, target_pos)
                self._update_with_obstacle_avoidance(npc, controller, steering)
        else:
            controller.steering_controller.last_safe_position = Vector2(npc.position)
    
    def execute_behavior(self, npc: NPC, behavior: Behavior, world_state: WorldState):
        """执行NPC的行为"""
        controller = self.npc_controllers[npc]
        
        target_pos = None
        nearest_enemy = None
        min_dist = float('inf')
        for enemy in self.enemies:
            if enemy.is_alive:
                dist = npc.position.distance_to(enemy.position)
                if dist < min_dist:
                    min_dist = dist
                    nearest_enemy = enemy
        
        if behavior == Behavior.Attack:
            if nearest_enemy:
                target_pos = nearest_enemy.position
        elif behavior == Behavior.Guard:
            if npc.guard_position:
                target_pos = npc.guard_position
        elif behavior == Behavior.Flee:
            if nearest_enemy:
                dx = npc.position.x - nearest_enemy.position.x
                dy = npc.position.y - nearest_enemy.position.y
                flee_x = npc.position.x + dx * 2
                flee_y = npc.position.y + dy * 2
                target_pos = Vector2(
                    max(50, min(flee_x, self.config.map.map_width - 50)),
                    max(50, min(flee_y, self.config.map.map_height - 50))
                )
        elif behavior == Behavior.Heal:
            if npc.heal_cooldown_remaining <= 0:
                npc.heal(self.config.npc.heal_amount)
                npc.heal_cooldown_remaining = self.config.npc.heal_cooldown
            target_pos = npc.guard_position if npc.guard_position else npc.position
        
        if target_pos:
            current_grid = self.grid.world_to_grid(npc.position)
            if not self.grid.is_walkable(current_grid[0], current_grid[1]):
                self._move_entity_to_walkable(npc)
            
            path = find_path(self.grid, npc.position, target_pos)
            if path:
                steering = controller.steering_controller.follow_path(npc.position, path)
                self._safe_update_position(npc, controller, steering, target_pos)
            else:
                steering = controller.steering_controller.seek(npc.position, target_pos)
                self._update_with_obstacle_avoidance(npc, controller, steering)
        
        if behavior == Behavior.Attack and nearest_enemy:
            self.combat_system.perform_attack(npc, nearest_enemy)
    
    def update_enemies(self):
        """更新敌人行为"""
        for enemy in self.enemies:
            if not enemy.is_alive:
                continue
            
            current_grid = self.grid.world_to_grid(enemy.position)
            if not self.grid.is_walkable(current_grid[0], current_grid[1]):
                self._move_entity_to_walkable(enemy)
            
            nearest_npc = None
            min_dist = float('inf')
            for npc in self.npcs:
                if npc.is_alive:
                    dist = enemy.position.distance_to(npc.position)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_npc = npc
            
            if nearest_npc:
                direction = nearest_npc.position - enemy.position
                if direction.x != 0 or direction.y != 0:
                    normalized = direction.normalized()
                    old_position = Vector2(enemy.position.x, enemy.position.y)
                    new_x = enemy.position.x + normalized.x * self.config.enemy.speed
                    new_y = enemy.position.y + normalized.y * self.config.enemy.speed
                    
                    test_pos = Vector2(new_x, new_y)
                    test_grid = self.grid.world_to_grid(test_pos)
                    if self.grid.is_walkable(test_grid[0], test_grid[1]):
                        enemy.position.x = new_x
                        enemy.position.y = new_y
                    else:
                        self._try_alternate_directions(enemy, normalized)
                    
                    enemy.position.x = max(50, min(enemy.position.x, self.config.map.map_width - 50))
                    enemy.position.y = max(50, min(enemy.position.y, self.config.map.map_height - 50))
                    enemy.look_at(nearest_npc.position)
                
                self.combat_system.perform_attack(enemy, nearest_npc)
            
            self.combat_system.update_cooldowns(enemy)
    
    def _try_alternate_directions(self, enemy, original_direction):
        """尝试多个替代方向避开障碍物
        
        Args:
            enemy: 敌人实体
            original_direction: 原始移动方向
        """
        test_directions = [
            Vector2(-original_direction.y, original_direction.x),
            Vector2(original_direction.y, -original_direction.x),
            Vector2(-original_direction.x, -original_direction.y),
            Vector2(original_direction.y, original_direction.x),
            Vector2(-original_direction.y, -original_direction.x),
        ]
        
        for dir in test_directions:
            if dir.x != 0 or dir.y != 0:
                normalized_dir = dir.normalized()
                new_x = enemy.position.x + normalized_dir.x * self.config.enemy.speed
                new_y = enemy.position.y + normalized_dir.y * self.config.enemy.speed
                
                test_pos = Vector2(new_x, new_y)
                test_grid = self.grid.world_to_grid(test_pos)
                if self.grid.is_walkable(test_grid[0], test_grid[1]):
                    enemy.position.x = new_x
                    enemy.position.y = new_y
                    return
    
    def _move_entity_to_walkable(self, entity):
        """将实体移动到最近的可通行位置
        
        Args:
            entity: 要移动的实体
        """
        current_grid = self.grid.world_to_grid(entity.position)
        grid_size = self.config.map.grid_size
        
        for radius in range(1, 5):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    check_x = current_grid[0] + dx
                    check_y = current_grid[1] + dy
                    if self.grid.is_walkable(check_x, check_y):
                        new_pos = self.grid.grid_to_world(check_x, check_y)
                        entity.position = new_pos
                        return
    
    def update(self):
        """游戏主更新逻辑"""
        self.frame_count += 1
        
        if self.frame_count % self.spawn_interval == 0:
            self.spawn_enemy()
        
        for npc in self.npcs:
            if not npc.is_alive:
                continue
            
            world_state = self.collect_world_state(npc)
            behavior = self.npc_controllers[npc].make_decision(world_state)
            npc.current_behavior = behavior
            self.execute_behavior(npc, behavior, world_state)
            self.combat_system.update_cooldowns(npc)
            
            if npc.heal_cooldown_remaining > 0:
                npc.heal_cooldown_remaining -= 1
        
        self.update_enemies()
        
        self.enemies = [e for e in self.enemies if e.is_alive]
    
    def render(self):
        """简单的渲染方法（仅输出状态信息）"""
        print(f"\n=== 游戏帧 {self.frame_count} ===")
        print(f"NPC数量: {len([n for n in self.npcs if n.is_alive])}")
        print(f"敌人数量: {len(self.enemies)}")
        print("\nNPC状态:")
        for npc in self.npcs:
            status = "存活" if npc.is_alive else "死亡"
            print(f"  {npc.name} [{npc.decision_type}]: HP={npc.hp:.0f}/{npc.max_hp:.0f}, 位置={npc.position}, 行为={npc.current_behavior.value} ({status})")
        print("\n敌人状态:")
        for enemy in self.enemies:
            print(f"  {enemy.name}: HP={enemy.hp:.0f}/{enemy.max_hp:.0f}, 位置={enemy.position}")
    
    def run(self, num_frames: int = 100):
        """运行游戏循环指定帧数"""
        self.is_running = True
        
        if self.use_gui and self.gui:
            print(f"开始游戏循环（GUI模式）...")
            self._run_gui_mode()
        else:
            print(f"开始游戏循环，运行 {num_frames} 帧...")
            self._run_headless_mode(num_frames)
        
        self.is_running = False
        if self.gui:
            self.gui.quit()
        print("\n游戏循环结束")
    
    def _run_headless_mode(self, num_frames: int):
        """无头模式运行（无GUI）"""
        for i in range(num_frames):
            self.update()
            if i % 20 == 0:
                self.render()
            
            if not any(npc.is_alive for npc in self.npcs):
                print("\n所有NPC已死亡，游戏结束")
                break
    
    def _run_gui_mode(self):
        """GUI模式运行"""
        self.is_running = True
        print("\n启动GUI模式...")
        print("控制:")
        print("  - 空格键: 暂停/继续")
        print("  - R键: 重置暂停")
        print()
        
        while self.is_running and self.gui.running:
            if not self.gui.game_paused:
                self.update()
            
            if not any(npc.is_alive for npc in self.npcs):
                print("\n所有NPC已死亡，游戏结束")
                break
            
            if self.gui:
                self.gui.handle_events()
                self.gui.render(self)
        
        if self.gui:
            self.gui.quit()


def test_game(use_gui: bool = True):
    """测试游戏循环"""
    print("=== 游戏系统测试 ===\n")
    
    config = GameConfig()
    game = Game(config, use_gui=use_gui)
    
    game.spawn_interval = 100
    game.spawn_enemy()
    
    if not use_gui:
        print("初始状态:")
        game.render()
        print("\n开始运行游戏循环 (50帧)...")
        game.run(50)
        print("\n最终状态:")
        game.render()
    else:
        print("开始运行游戏循环 (GUI模式)...")
        game.run()
    
    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    test_game()
