import math
from typing import List, Optional


class Vector2:
    """2D向量类
    
    用于表示2D空间中的位置和方向
    """
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        """初始化2D向量
        
        Args:
            x: X坐标
            y: Y坐标
        """
        self.x = x  # X坐标
        self.y = y  # Y坐标

    def distance_to(self, other: 'Vector2') -> float:
        """计算到另一个向量的距离
        
        Args:
            other: 目标向量
            
        Returns:
            两点之间的欧几里得距离
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def __sub__(self, other: 'Vector2') -> 'Vector2':
        """向量减法"""
        return Vector2(self.x - other.x, self.y - other.y)

    def __add__(self, other: 'Vector2') -> 'Vector2':
        """向量加法"""
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        """向量标量乘法"""
        return Vector2(self.x * scalar, self.y * scalar)

    def normalized(self) -> 'Vector2':
        """获取归一化的向量
        
        Returns:
            单位长度的向量
        """
        length = math.sqrt(self.x * self.x + self.y * self.y)
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"Vector2({self.x:.1f}, {self.y:.1f})"


class GameEntity:
    """游戏实体基类
    
    所有游戏中存在的实体的基类
    """
    
    def __init__(self, name: str, position: Vector2):
        """初始化游戏实体
        
        Args:
            name: 实体名称
            position: 实体位置
        """
        self.name = name  # 实体名称
        self.position = position  # 实体位置
        self.rotation = 0.0  # 朝向角度（弧度）

    def look_at(self, target: Vector2) -> None:
        """让实体面朝目标位置
        
        Args:
            target: 目标位置
        """
        direction = target - self.position
        if direction.x != 0 or direction.y != 0:
            self.rotation = math.atan2(direction.y, direction.x)

    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.name} at {self.position}"


class Character(GameEntity):
    """角色类
    
    具有血量系统的游戏实体
    """
    
    def __init__(self, name: str, position: Vector2, max_hp: float = 100.0):
        """初始化角色
        
        Args:
            name: 角色名称
            position: 角色位置
            max_hp: 最大血量
        """
        super().__init__(name, position)
        self.max_hp = max_hp  # 最大血量
        self.hp = max_hp  # 当前血量
        self.is_alive = True  # 是否存活

    def take_damage(self, amount: float) -> None:
        """受到伤害
        
        Args:
            amount: 伤害值
        """
        if not self.is_alive:
            return
        self.hp = max(0, self.hp - amount)
        if self.hp <= 0:
            self.is_alive = False
            self.hp = 0

    def heal(self, amount: float) -> None:
        """治疗
        
        Args:
            amount: 治疗量
        """
        if not self.is_alive:
            return
        self.hp = min(self.max_hp, self.hp + amount)

    def hp_percentage(self) -> float:
        """获取血量百分比
        
        Returns:
            血量百分比（0-1）
        """
        return self.hp / self.max_hp if self.max_hp > 0 else 0.0

    def __repr__(self) -> str:
        """字符串表示"""
        return f"{self.name} (HP: {self.hp:.0f}/{self.max_hp:.0f}) at {self.position}"


class Player(Character):
    """玩家类"""
    
    def __init__(self, position: Vector2 = Vector2(0, 0)):
        """初始化玩家
        
        Args:
            position: 玩家位置
        """
        super().__init__("Player", position)


class Enemy(Character):
    """敌人类"""
    
    def __init__(self, name: str = "Enemy", position: Vector2 = Vector2(0, 0), max_hp: float = 50.0):
        """初始化敌人
        
        Args:
            name: 敌人名称
            position: 敌人位置
            max_hp: 最大血量
        """
        super().__init__(name, position, max_hp)


class Teammate(Character):
    """AI队友类"""
    
    def __init__(self, name: str = "Teammate", position: Vector2 = Vector2(0, 0), max_hp: float = 100.0):
        """初始化AI队友
        
        Args:
            name: 队友名称
            position: 队友位置
            max_hp: 最大血量
        """
        super().__init__(name, position, max_hp)
        self.healing_potion_count = 3  # 治疗药水数量
        self.current_behavior = "Idle"  # 当前行为

    def use_healing_potion(self) -> bool:
        """使用治疗药水
        
        Returns:
            是否成功使用
        """
        if self.healing_potion_count > 0:
            self.healing_potion_count -= 1
            self.heal(50)
            return True
        return False
