from dataclasses import dataclass
from typing import Optional, Dict
from .entities import Behavior, Vector2
from .config import UtilityWeights


@dataclass
class WorldState:
    """世界状态类，包含决策所需的所有信息"""
    
    my_health: float = 1.0
    """自身血量（归一化到0-1）"""
    
    enemy_threat: float = 0.0
    """敌人威胁（归一化到0-1）"""
    
    enemy_count: float = 0.0
    """敌人数量（归一化到0-1）"""
    
    ammo_level: float = 1.0
    """弹药量（归一化到0-1）"""
    
    safe_area: float = 1.0
    """安全区域（归一化到0-1）"""
    
    distance_to_guard_point: float = 1.0
    """到警戒点的距离（归一化到0-1）"""
    
    guard_point: Optional[Vector2] = None
    """警戒点位置"""


class UtilityAI:
    """Utility AI决策系统类"""
    
    def __init__(self, weights: Optional[UtilityWeights] = None):
        """初始化Utility AI决策系统
        
        Args:
            weights: 评分权重配置，如果为None则使用默认权重
        """
        self.weights = weights if weights else UtilityWeights()
    
    def _normalize(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """将值归一化到[0, 1]范围
        
        Args:
            value: 需要归一化的值
            min_val: 最小值
            max_val: 最大值
            
        Returns:
            归一化后的值
        """
        if max_val == min_val:
            return 0.0
        normalized = (value - min_val) / (max_val - min_val)
        return max(0.0, min(1.0, normalized))
    
    def calculate_attack_score(self, world_state: WorldState) -> float:
        """计算攻击行为的评分
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            攻击行为的评分
        """
        return (world_state.enemy_threat * self.weights.attack_enemy_threat_weight +
                world_state.my_health * self.weights.attack_my_health_weight +
                world_state.ammo_level * self.weights.attack_ammo_level_weight)
    
    def calculate_heal_score(self, world_state: WorldState) -> float:
        """计算治疗行为的评分
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            治疗行为的评分
        """
        return ((1 - world_state.my_health) * self.weights.heal_my_health_weight +
                world_state.safe_area * self.weights.heal_safe_area_weight)
    
    def calculate_flee_score(self, world_state: WorldState) -> float:
        """计算逃跑行为的评分
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            逃跑行为的评分
        """
        return ((1 - world_state.my_health) * self.weights.flee_my_health_weight +
                world_state.enemy_count * self.weights.flee_enemy_count_weight +
                world_state.enemy_threat * self.weights.flee_enemy_threat_weight)
    
    def calculate_guard_score(self, world_state: WorldState) -> float:
        """计算守卫行为的评分
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            守卫行为的评分
        """
        return world_state.distance_to_guard_point * self.weights.guard_proximity_weight
    
    def calculate_all_scores(self, world_state: WorldState) -> Dict[Behavior, float]:
        """计算所有行为的评分
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            包含所有行为评分的字典
        """
        scores = {
            Behavior.Attack: self.calculate_attack_score(world_state),
            Behavior.Heal: self.calculate_heal_score(world_state),
            Behavior.Flee: self.calculate_flee_score(world_state),
            Behavior.Guard: self.calculate_guard_score(world_state)
        }
        return scores
    
    def decide(self, world_state: WorldState) -> Behavior:
        """根据世界状态选择最优行为
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            选择的行为
        """
        scores = self.calculate_all_scores(world_state)
        return max(scores, key=scores.get)


def test_utility_ai():
    """测试Utility AI的评分逻辑"""
    
    print("=== Utility AI 测试 ===")
    
    ai = UtilityAI()
    
    print("\n1. 测试攻击场景（高威胁，满血，弹药充足）")
    attack_state = WorldState(
        my_health=1.0,
        enemy_threat=0.9,
        enemy_count=0.5,
        ammo_level=1.0,
        safe_area=0.3,
        distance_to_player=0.8,
        distance_to_guard_point=0.7
    )
    attack_scores = ai.calculate_all_scores(attack_state)
    chosen_behavior = ai.decide(attack_state)
    print(f"   评分: {attack_scores}")
    print(f"   选择的行为: {chosen_behavior}")
    assert chosen_behavior == Behavior.Attack, "应该选择攻击行为"
    print("   ✓ 通过")
    
    print("\n2. 测试治疗场景（低血量，在安全区域）")
    heal_state = WorldState(
        my_health=0.2,
        enemy_threat=0.1,
        enemy_count=0.0,
        ammo_level=0.5,
        safe_area=1.0,
        distance_to_player=0.5,
        distance_to_guard_point=0.5
    )
    heal_scores = ai.calculate_all_scores(heal_state)
    chosen_behavior = ai.decide(heal_state)
    print(f"   评分: {heal_scores}")
    print(f"   选择的行为: {chosen_behavior}")
    assert chosen_behavior == Behavior.Heal, "应该选择治疗行为"
    print("   ✓ 通过")
    
    print("\n3. 测试逃跑场景（低血量，高威胁，多个敌人）")
    flee_state = WorldState(
        my_health=0.1,
        enemy_threat=0.9,
        enemy_count=0.8,
        ammo_level=0.2,
        safe_area=0.2,
        distance_to_player=0.3,
        distance_to_guard_point=0.4
    )
    flee_scores = ai.calculate_all_scores(flee_state)
    chosen_behavior = ai.decide(flee_state)
    print(f"   评分: {flee_scores}")
    print(f"   选择的行为: {chosen_behavior}")
    assert chosen_behavior == Behavior.Flee, "应该选择逃跑行为"
    print("   ✓ 通过")
    
    print("\n4. 测试跟随玩家场景（离玩家较远，无威胁）")
    follow_state = WorldState(
        my_health=1.0,
        enemy_threat=0.0,
        enemy_count=0.0,
        ammo_level=0.0,
        safe_area=0.0,
        distance_to_player=0.9,
        distance_to_guard_point=0.1
    )
    follow_scores = ai.calculate_all_scores(follow_state)
    chosen_behavior = ai.decide(follow_state)
    print(f"   评分: {follow_scores}")
    print(f"   选择的行为: {chosen_behavior}")
    assert chosen_behavior == Behavior.FollowPlayer, "应该选择跟随玩家行为"
    print("   ✓ 通过")
    
    print("\n5. 测试守卫场景（离警戒点较远，无威胁）")
    guard_state = WorldState(
        my_health=1.0,
        enemy_threat=0.0,
        enemy_count=0.0,
        ammo_level=0.0,
        safe_area=0.0,
        distance_to_player=0.1,
        distance_to_guard_point=0.9,
        guard_point=Vector2(400, 300)
    )
    guard_scores = ai.calculate_all_scores(guard_state)
    chosen_behavior = ai.decide(guard_state)
    print(f"   评分: {guard_scores}")
    print(f"   选择的行为: {chosen_behavior}")
    assert chosen_behavior == Behavior.Guard, "应该选择守卫行为"
    print("   ✓ 通过")
    
    print("\n6. 测试自定义权重")
    custom_weights = UtilityWeights(
        attack_enemy_threat_weight=0.9,
        attack_my_health_weight=0.05,
        attack_ammo_level_weight=0.05
    )
    custom_ai = UtilityAI(custom_weights)
    custom_state = WorldState(
        my_health=0.5,
        enemy_threat=0.8,
        enemy_count=0.3,
        ammo_level=0.5
    )
    score = custom_ai.calculate_attack_score(custom_state)
    print(f"   自定义权重攻击评分: {score}")
    print("   ✓ 通过")
    
    print("\n=== 所有测试通过 ===")


if __name__ == "__main__":
    test_utility_ai()
