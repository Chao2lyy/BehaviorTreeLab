import math
from typing import List, Optional, Tuple
from .entities import Vector2, GameEntity, Character
from .config import GameConfig


class SteeringAcceleration:
    """转向加速度数据类
    
    存储线性加速度和角加速度
    """
    
    def __init__(self, linear: Vector2 = Vector2(0, 0), angular: float = 0.0):
        """初始化转向加速度
        
        Args:
            linear: 线性加速度
            angular: 角加速度
        """
        self.linear = linear
        self.angular = angular
    
    def __repr__(self) -> str:
        return f"SteeringAcceleration(linear={self.linear}, angular={self.angular:.2f})"


class SteeringBehaviors:
    """Steering行为类
    
    实现各种Steering行为
    """
    
    def __init__(self, config: GameConfig):
        """初始化Steering行为
        
        Args:
            config: 游戏配置
        """
        self.config = config
    
    def seek(self, current_pos: Vector2, current_velocity: Vector2, 
             target_pos: Vector2, max_speed: float, max_acceleration: float) -> SteeringAcceleration:
        """Seek追逐行为：计算向目标移动的加速度
        
        Args:
            current_pos: 当前位置
            current_velocity: 当前速度
            target_pos: 目标位置
            max_speed: 最大速度
            max_acceleration: 最大加速度
            
        Returns:
            转向加速度
        """
        result = SteeringAcceleration()
        
        direction = target_pos - current_pos
        result.linear = direction.normalized() * max_acceleration
        
        return result
    
    def flee(self, current_pos: Vector2, current_velocity: Vector2,
             target_pos: Vector2, max_speed: float, max_acceleration: float) -> SteeringAcceleration:
        """Flee逃离行为：计算远离目标的加速度
        
        Args:
            current_pos: 当前位置
            current_velocity: 当前速度
            target_pos: 目标位置（逃离源）
            max_speed: 最大速度
            max_acceleration: 最大加速度
            
        Returns:
            转向加速度
        """
        result = SteeringAcceleration()
        
        direction = current_pos - target_pos
        result.linear = direction.normalized() * max_acceleration
        
        return result
    
    def path_following(self, current_pos: Vector2, current_velocity: Vector2,
                       path: List[Vector2], current_path_index: int,
                       max_speed: float, max_acceleration: float,
                       waypoint_radius: float = 30.0) -> Tuple[SteeringAcceleration, int]:
        """路径跟随行为：沿路径点列表移动
        
        Args:
            current_pos: 当前位置
            current_velocity: 当前速度
            path: 路径点列表
            current_path_index: 当前路径点索引
            max_speed: 最大速度
            max_acceleration: 最大加速度
            waypoint_radius: 路点到达半径
            
        Returns:
            (转向加速度, 更新后的路径点索引)
        """
        result = SteeringAcceleration()
        
        if not path or current_path_index >= len(path):
            return result, current_path_index
        
        target_waypoint = path[current_path_index]
        
        if current_pos.distance_to(target_waypoint) < waypoint_radius:
            current_path_index += 1
            if current_path_index >= len(path):
                return result, current_path_index
            target_waypoint = path[current_path_index]
        
        return self.seek(current_pos, current_velocity, target_waypoint, 
                        max_speed, max_acceleration), current_path_index


class SteeringController:
    """转向控制器类
    
    整合处理移动逻辑，应用于实体
    """
    
    def __init__(self, config: GameConfig):
        """初始化转向控制器
        
        Args:
            config: 游戏配置
        """
        self.config = config
        self.behaviors = SteeringBehaviors(config)
        self.velocity: Vector2 = Vector2(0, 0)
        self.max_speed: float = 0.0
        self.max_acceleration: float = 0.0
        self.current_path: List[Vector2] = []
        self.current_path_index: int = 0
        self.last_safe_position: Optional[Vector2] = None
    
    def attach_to_character(self, character: Character, speed: Optional[float] = None):
        """将控制器附加到角色
        
        Args:
            character: 角色实体
            speed: 可选的速度配置，默认使用配置文件中的速度
        """
        if speed is not None:
            self.max_speed = speed
        else:
            self.max_speed = self.config.npc.speed
        
        self.max_acceleration = self.max_speed * 2.0
        self.velocity = Vector2(0, 0)
        self.last_safe_position = Vector2(character.position.x, character.position.y)
    
    def update(self, entity: GameEntity, steering: SteeringAcceleration, 
              map_width: float, map_height: float, dt: float = 1.0):
        """更新实体位置和速度
        
        Args:
            entity: 游戏实体
            steering: 转向加速度
            map_width: 地图宽度（用于边界检测）
            map_height: 地图高度（用于边界检测）
            dt: 时间增量
        """
        self.velocity = self.velocity + steering.linear * dt
        
        self._limit_velocity()
        
        new_pos = entity.position + self.velocity * dt
        
        new_pos = self._apply_bounds(new_pos, map_width, map_height)
        
        entity.position = new_pos
        
        if self.velocity.x != 0 or self.velocity.y != 0:
            entity.look_at(entity.position + self.velocity)
    
    def _limit_velocity(self):
        """限制速度在最大速度范围内"""
        speed = math.sqrt(self.velocity.x * self.velocity.x + self.velocity.y * self.velocity.y)
        if speed > self.max_speed and speed > 0:
            self.velocity = self.velocity * (self.max_speed / speed)
    
    def _apply_bounds(self, position: Vector2, map_width: float, map_height: float) -> Vector2:
        """应用边界检测，确保角色不会移出地图
        
        Args:
            position: 当前位置
            map_width: 地图宽度
            map_height: 地图高度
            
        Returns:
            限制在地图范围内的位置
        """
        margin = 20.0
        new_x = max(margin, min(position.x, map_width - margin))
        new_y = max(margin, min(position.y, map_height - margin))
        
        if new_x != position.x:
            self.velocity.x = 0
        if new_y != position.y:
            self.velocity.y = 0
        
        return Vector2(new_x, new_y)
    
    def seek(self, current_pos: Vector2, target_pos: Vector2) -> SteeringAcceleration:
        """执行Seek行为
        
        Args:
            current_pos: 当前位置
            target_pos: 目标位置
            
        Returns:
            转向加速度
        """
        return self.behaviors.seek(current_pos, self.velocity, target_pos, 
                                   self.max_speed, self.max_acceleration)
    
    def flee(self, current_pos: Vector2, threat_pos: Vector2) -> SteeringAcceleration:
        """执行Flee行为
        
        Args:
            current_pos: 当前位置
            threat_pos: 威胁位置
            
        Returns:
            转向加速度
        """
        return self.behaviors.flee(current_pos, self.velocity, threat_pos, 
                                   self.max_speed, self.max_acceleration)
    
    def follow_path(self, current_pos: Vector2, path: Optional[List[Vector2]] = None) -> SteeringAcceleration:
        """执行路径跟随行为
        
        Args:
            current_pos: 当前位置
            path: 可选的路径，若提供则更新当前路径
            
        Returns:
            转向加速度
        """
        if path is not None:
            self.current_path = path
            self.current_path_index = 0
        
        steering, new_index = self.behaviors.path_following(
            current_pos, self.velocity, self.current_path, 
            self.current_path_index, self.max_speed, self.max_acceleration
        )
        self.current_path_index = new_index
        
        return steering
    
    def stop(self):
        """停止移动"""
        self.velocity = Vector2(0, 0)
