import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from dataclasses import dataclass
from typing import Optional
from behavior_tree import (
    NodeStatus,
    Blackboard,
    Action,
    Condition,
    Sequence,
    Selector,
)

try:
    from .entities import Behavior
    from .config import NPCConfig
except ImportError:
    from examples.ai_behavior_research.entities import Behavior
    from examples.ai_behavior_research.config import NPCConfig


@dataclass
class WorldState:
    """世界状态类，包含行为树决策所需的所有信息"""
    
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


class BTNPC:
    """行为树NPC类
    
    使用行为树控制NPC的决策
    
    与FSM和Utility AI的主要区别：
    - FSM：硬编码的状态转换，状态机模式
    - Utility AI：基于连续评分，选择最高分行为
    - 行为树：树状结构组织，选择器和顺序器组合，易于扩展和调试
    """
    
    def __init__(self, config: Optional[NPCConfig] = None):
        """初始化行为树NPC
        
        Args:
            config: NPC配置，如果为None则使用默认配置
        """
        self.config = config if config else NPCConfig()
        self.blackboard = Blackboard()
        self.current_behavior: Behavior = Behavior.Guard
        self._world_state: Optional[WorldState] = None
        self._build_behavior_tree()
    
    def _build_behavior_tree(self):
        """构建行为树
        
        行为树结构：
        Root (Selector)
        ├── Emergency Sequence (治疗紧急情况)
        │   ├── Condition: 低血量且在安全区域且治疗可用
        │   └── Action: 执行治疗
        ├── Combat Sequence (战斗情况)
        │   ├── Condition: 有敌人且威胁高
        │   └── Action: 攻击敌人
        ├── Flee Sequence (逃跑情况)
        │   ├── Condition: 低血量且威胁高
        │   └── Action: 逃离敌人
        └── Idle Action (待机)
        """
        """条件检查函数"""
        
        def is_emergency_heal_needed():
            """检查是否需要紧急治疗 - 行为树更保守，更早治疗"""
            ws = self._world_state
            if not ws:
                return False
            return ws.my_health < 0.6 and ws.in_safe_area and ws.heal_available
        
        def is_combat_needed():
            """检查是否需要战斗 - 行为树更保守，需要更高威胁才攻击"""
            ws = self._world_state
            if not ws:
                return False
            return ws.enemy_distance < 0.5 and ws.enemy_threat > 0.6
        
        def is_flee_needed():
            """检查是否需要逃跑 - 行为树更保守，更早逃跑"""
            ws = self._world_state
            if not ws:
                return False
            return ws.my_health < 0.5 and ws.enemy_threat > 0.4
        
        """动作执行函数"""
        
        def execute_heal():
            """执行治疗动作"""
            self.current_behavior = Behavior.Heal
            self.blackboard.set("last_behavior", "Heal")
            return NodeStatus.SUCCESS
        
        def execute_attack():
            """执行攻击动作"""
            self.current_behavior = Behavior.Attack
            self.blackboard.set("last_behavior", "Attack")
            return NodeStatus.SUCCESS
        
        def execute_flee():
            """执行逃跑动作"""
            self.current_behavior = Behavior.Flee
            self.blackboard.set("last_behavior", "Flee")
            return NodeStatus.SUCCESS
        
        def execute_idle():
            """执行待机动作"""
            self.current_behavior = Behavior.Guard
            self.blackboard.set("last_behavior", "Guard")
            return NodeStatus.SUCCESS
        
        """构建各个分支"""
        emergency_behavior = Sequence([
            Condition(is_emergency_heal_needed),
            Action(execute_heal),
        ], name="紧急治疗")
        
        combat_behavior = Sequence([
            Condition(is_combat_needed),
            Action(execute_attack),
        ], name="战斗")
        
        flee_behavior = Sequence([
            Condition(is_flee_needed),
            Action(execute_flee),
        ], name="逃跑")
        
        idle_behavior = Action(execute_idle, name="待机")
        
        """根选择器 - 行为树更保守，把逃跑和治疗优先级更高"""
        self.root = Selector([
            flee_behavior,
            emergency_behavior,
            combat_behavior,
            idle_behavior,
        ], name="Root")
        
        self.root.blackboard = self.blackboard
    
    def tick(self, world_state: WorldState) -> Behavior:
        """执行一次行为树更新
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            选择的行为
        """
        self._world_state = world_state
        self.blackboard.set("world_state", world_state)
        self.root.tick()
        return self.current_behavior
    
    def get_current_behavior(self) -> Behavior:
        """获取当前行为
        
        Returns:
            当前行为
        """
        return self.current_behavior


def test_bt_npc():
    """测试行为树NPC的决策逻辑"""
    
    print("=== 行为树 NPC 测试 ===")
    
    npc = BTNPC()
    
    print(f"\n初始行为: {npc.get_current_behavior()}")
    assert npc.get_current_behavior() == Behavior.Guard, "初始行为应该是Guard"
    
    print("\n1. 测试紧急治疗场景（低血量，安全区域，治疗可用）")
    state1 = WorldState(
        my_health=0.3,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.3,
        in_safe_area=True,
        heal_available=True
    )
    behavior = npc.tick(state1)
    print(f"   行为: {behavior}")
    assert behavior == Behavior.Heal, "应该选择治疗行为"
    
    print("\n2. 测试逃跑场景（低血量，高威胁）")
    state2 = WorldState(
        my_health=0.2,
        enemy_distance=0.4,
        enemy_threat=0.8,
        enemy_count=2,
        distance_to_player=0.3,
        in_safe_area=False,
        heal_available=True
    )
    behavior = npc.tick(state2)
    print(f"   行为: {behavior}")
    assert behavior == Behavior.Flee, "应该选择逃跑行为"
    
    print("\n3. 测试战斗场景（敌人接近，威胁高，血量适中）")
    state3 = WorldState(
        my_health=0.8,
        enemy_distance=0.5,
        enemy_threat=0.7,
        enemy_count=1,
        distance_to_player=0.2,
        in_safe_area=True,
        heal_available=True
    )
    behavior = npc.tick(state3)
    print(f"   行为: {behavior}")
    assert behavior == Behavior.Attack, "应该选择攻击行为"
    
    print("\n4. 测试跟随场景（离玩家较远，无威胁）")
    state4 = WorldState(
        my_health=0.9,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.8,
        in_safe_area=True,
        heal_available=True
    )
    behavior = npc.tick(state4)
    print(f"   行为: {behavior}")
    assert behavior == Behavior.FollowPlayer, "应该选择跟随行为"
    
    print("\n5. 测试待机场景（无特殊情况）")
    state5 = WorldState(
        my_health=1.0,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.3,
        in_safe_area=True,
        heal_available=True
    )
    behavior = npc.tick(state5)
    print(f"   行为: {behavior}")
    assert behavior == Behavior.Guard, "应该选择守卫(待机)行为"
    
    print("\n=== 三种决策方式对比 ===")
    print("1. FSM: 硬编码状态转换，明确状态，易于理解和调试")
    print("2. Utility AI: 连续评分函数，灵活权衡，平滑过渡")
    print("3. 行为树: 树状组合结构，模块化设计，易于扩展和复用")
    print("\n行为树特点:")
    print("  - 使用Selector按优先级选择行为分支")
    print("  - 使用Sequence确保条件和动作顺序执行")
    print("  - 使用Blackboard在节点间共享数据")
    print("  - 行为树结构可视化，便于调试和理解")
    
    print("\n=== 所有测试通过 ===")


if __name__ == "__main__":
    test_bt_npc()
