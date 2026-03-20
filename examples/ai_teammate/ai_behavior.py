import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from behavior_tree import (
    NodeStatus,
    Blackboard,
    Action,
    Condition,
    Sequence,
    Selector,
)
from .entities import Teammate, Player, Enemy, Vector2


class AITeammate:
    """AI队友类
    
    使用行为树控制AI队友的行为
    """
    
    def __init__(self, teammate: Teammate, player: Player, blackboard: Blackboard, config=None):
        """初始化AI队友
        
        Args:
            teammate: AI队友实体
            player: 玩家实体
            blackboard: 黑板对象
            config: AI队友配置
        """
        self.teammate = teammate  # AI队友实体
        self.player = player  # 玩家实体
        self.blackboard = blackboard  # 黑板对象
        self.enemies: list[Enemy] = []  # 敌人列表
        self.attack_cooldown = 0  # AI攻击冷却时间
        self.config = config  # AI队友配置
        self._build_behavior_tree()  # 构建行为树

    def _build_behavior_tree(self):
        """构建行为树
        
        按照配置的优先级顺序构建行为
        """
        # 获取配置参数
        low_hp_threshold = self.config.low_hp_threshold if self.config else 0.3
        detection_range = self.config.detection_range if self.config else 200.0
        melee_range = self.config.melee_range if self.config else 80.0
        follow_distance = self.config.follow_distance if self.config else 100.0
        speed = self.config.speed if self.config else 2.5
        melee_damage = self.config.melee_damage if self.config else 15.0
        ranged_damage = self.config.ranged_damage if self.config else 10.0
        melee_cooldown = self.config.melee_cooldown if self.config else 45
        ranged_cooldown = self.config.ranged_cooldown if self.config else 60
        behavior_priority = self.config.behavior_priority if self.config else ['emergency', 'combat', 'follow', 'idle']

        # 紧急治疗行为
        def is_low_hp():
            """检查血量是否低于阈值"""
            return self.teammate.hp_percentage() < low_hp_threshold

        def use_healing_potion():
            """使用治疗药水"""
            if self.teammate.use_healing_potion():
                self.teammate.current_behavior = "紧急治疗"
                return NodeStatus.SUCCESS
            return NodeStatus.FAILURE

        emergency_behavior = Sequence([
            Condition(is_low_hp),
            Action(use_healing_potion),
        ], name="紧急行为")

        # 战斗行为
        def has_nearby_enemy():
            """检查附近是否有敌人"""
            for enemy in self.enemies:
                if enemy.is_alive and self.teammate.position.distance_to(enemy.position) < detection_range:
                    self.blackboard.set("target_enemy", enemy)
                    return True
            return False

        def face_enemy():
            """面朝敌人"""
            enemy = self.blackboard.get("target_enemy")
            if enemy:
                self.teammate.look_at(enemy.position)
            return NodeStatus.SUCCESS

        def try_attack_or_move():
            """尝试攻击或移动"""
            enemy = self.blackboard.get("target_enemy")
            if not enemy or not enemy.is_alive:
                return NodeStatus.FAILURE
            
            dist = self.teammate.position.distance_to(enemy.position)
            
            # 尝试近战攻击
            if dist < melee_range:
                if self.attack_cooldown <= 0:
                    enemy.take_damage(melee_damage)
                    self.teammate.current_behavior = "近战攻击"
                    self.attack_cooldown = melee_cooldown
                else:
                    self.teammate.current_behavior = "等待攻击冷却"
                return NodeStatus.SUCCESS
            
            # 尝试远程攻击
            if self.attack_cooldown <= 0:
                enemy.take_damage(ranged_damage)
                self.teammate.current_behavior = "远程攻击"
                self.attack_cooldown = ranged_cooldown
                return NodeStatus.SUCCESS
            
            # 向敌人移动
            direction = enemy.position - self.teammate.position
            direction = direction.normalized()
            self.teammate.position = self.teammate.position + direction * speed
            self.teammate.current_behavior = "向敌人移动"
            return NodeStatus.SUCCESS

        combat_behavior = Sequence([
            Condition(has_nearby_enemy),
            Action(try_attack_or_move),
            Action(face_enemy),
        ], name="战斗行为")

        # 跟随行为
        def is_far_from_player():
            """检查是否距离玩家较远"""
            return self.teammate.position.distance_to(self.player.position) > follow_distance

        def move_to_player():
            """移动到玩家附近"""
            direction = self.player.position - self.teammate.position
            direction = direction.normalized()
            self.teammate.position = self.teammate.position + direction * speed
            self.teammate.current_behavior = "跟随玩家"
            return NodeStatus.SUCCESS

        follow_behavior = Sequence([
            Condition(is_far_from_player),
            Action(move_to_player),
        ], name="跟随行为")

        # 待机行为
        def idle_animation():
            """待机动画"""
            self.teammate.current_behavior = "待机"
            return NodeStatus.SUCCESS

        idle_behavior = Action(idle_animation, name="待机行为")

        # 构建行为映射
        behavior_map = {
            'emergency': emergency_behavior,
            'combat': combat_behavior,
            'follow': follow_behavior,
            'idle': idle_behavior
        }

        # 根据优先级顺序构建根节点
        ordered_behaviors = []
        for behavior_name in behavior_priority:
            if behavior_name in behavior_map:
                ordered_behaviors.append(behavior_map[behavior_name])

        # 根节点（按配置的优先级选择）
        self.root = Selector(ordered_behaviors, name="Root")

        self.root.blackboard = self.blackboard

    def update(self):
        """更新AI行为
        
        Returns:
            行为树执行状态
        """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        return self.root.tick()

    def add_enemy(self, enemy: Enemy):
        """添加敌人
        
        Args:
            enemy: 要添加的敌人
        """
        self.enemies.append(enemy)
