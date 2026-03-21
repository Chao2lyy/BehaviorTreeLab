from enum import Enum
from typing import Optional, Dict, Callable
from dataclasses import dataclass
from .entities import Vector2, Character
from .config import NPCConfig


class FSMState(Enum):
    """FSM状态枚举类"""
    Idle = "Idle"
    Attack = "Attack"
    Flee = "Flee"
    Heal = "Heal"


@dataclass
class WorldState:
    """世界状态类，包含FSM决策所需的所有信息"""
    
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


class FSMNPC:
    """有限状态机NPC类"""
    
    def __init__(self, config: Optional[NPCConfig] = None):
        """初始化FSM NPC
        
        Args:
            config: NPC配置，如果为None则使用默认配置
        """
        self.config = config if config else NPCConfig()
        self.current_state: FSMState = FSMState.Idle
        self.previous_state: Optional[FSMState] = None
        self.state_transitions: Dict[FSMState, Dict[FSMState, Callable[[WorldState], bool]]] = {}
        self.state_actions: Dict[FSMState, Callable[[WorldState], str]] = {}
        self._setup_transitions()
        self._setup_actions()
    
    def _setup_transitions(self):
        """设置状态转换规则 - FSM配置为更激进的策略
        
        FSM特点：
        - 更主动攻击：更早发现敌人就攻击
        - 更不容易逃跑：低血量时仍坚持战斗
        - 更少治疗：更倾向于战斗而非治疗
        """
        
        self.state_transitions = {
            FSMState.Idle: {
                FSMState.Attack: lambda ws: ws.enemy_distance < 0.8 and ws.enemy_threat > 0.1,
                FSMState.Heal: lambda ws: ws.my_health < 0.3 and ws.heal_available and ws.in_safe_area
            },
            FSMState.Attack: {
                FSMState.Flee: lambda ws: ws.my_health < 0.15 and ws.enemy_threat > 0.8,
                FSMState.Heal: lambda ws: ws.my_health < 0.2 and ws.in_safe_area and ws.heal_available,
                FSMState.Idle: lambda ws: ws.enemy_distance > 0.95
            },
            FSMState.Flee: {
                FSMState.Attack: lambda ws: ws.my_health > 0.25 or ws.enemy_threat < 0.4,
                FSMState.Heal: lambda ws: ws.my_health < 0.25 and ws.in_safe_area and ws.heal_available,
                FSMState.Idle: lambda ws: ws.in_safe_area and ws.enemy_distance > 0.9
            },
            FSMState.Heal: {
                FSMState.Attack: lambda ws: ws.my_health >= 0.4 or ws.enemy_threat > 0.3,
                FSMState.Flee: lambda ws: ws.enemy_threat > 0.8 and not ws.in_safe_area,
                FSMState.Idle: lambda ws: ws.my_health >= 0.95 or not ws.heal_available
            }
        }
    
    def _setup_actions(self):
        """设置各状态的行为逻辑"""
        
        self.state_actions = {
            FSMState.Idle: lambda ws: "等待中，保持警戒",
            FSMState.Attack: lambda ws: f"攻击敌人，威胁等级: {ws.enemy_threat:.2f}",
            FSMState.Flee: lambda ws: f"逃离敌人，当前血量: {ws.my_health:.2f}",
            FSMState.Heal: lambda ws: f"治疗自己，当前血量: {ws.my_health:.2f}"
        }
    
    def _check_transitions(self, world_state: WorldState) -> Optional[FSMState]:
        """检查是否有满足条件的状态转换
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            新的状态，如果没有满足条件的转换则返回None
        """
        if self.current_state not in self.state_transitions:
            return None
        
        transitions = self.state_transitions[self.current_state]
        
        for target_state, condition in transitions.items():
            if condition(world_state):
                return target_state
        
        return None
    
    def _on_enter_state(self, new_state: FSMState, world_state: WorldState) -> None:
        """进入新状态时的回调
        
        Args:
            new_state: 新状态
            world_state: 世界状态信息
        """
        pass
    
    def _on_exit_state(self, old_state: FSMState, world_state: WorldState) -> None:
        """离开旧状态时的回调
        
        Args:
            old_state: 旧状态
            world_state: 世界状态信息
        """
        pass
    
    def update(self, world_state: WorldState) -> str:
        """更新FSM状态并返回行为描述
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            当前状态的行为描述
        """
        new_state = self._check_transitions(world_state)
        
        if new_state and new_state != self.current_state:
            self._on_exit_state(self.current_state, world_state)
            self.previous_state = self.current_state
            self.current_state = new_state
            self._on_enter_state(new_state, world_state)
        
        return self._execute_action(world_state)
    
    def _execute_action(self, world_state: WorldState) -> str:
        """执行当前状态的行为
        
        Args:
            world_state: 世界状态信息
            
        Returns:
            行为描述
        """
        if self.current_state in self.state_actions:
            return self.state_actions[self.current_state](world_state)
        return "无行为"
    
    def get_current_state(self) -> FSMState:
        """获取当前状态
        
        Returns:
            当前状态
        """
        return self.current_state


def test_fsm_npc():
    """测试FSM NPC的状态转换逻辑"""
    
    print("=== FSM NPC 测试 ===")
    
    npc = FSMNPC()
    
    print(f"\n初始状态: {npc.get_current_state()}")
    assert npc.get_current_state() == FSMState.Idle, "初始状态应该是Idle"
    
    print("\n1. 测试 Idle -> Attack 转换（敌人接近）")
    state1 = WorldState(
        my_health=1.0,
        enemy_distance=0.5,
        enemy_threat=0.7,
        enemy_count=1,
        distance_to_player=0.2,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state1)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Attack, "应该转换到Attack状态"
    
    print("\n2. 测试 Attack -> Flee 转换（低血量高威胁）")
    state2 = WorldState(
        my_health=0.2,
        enemy_distance=0.4,
        enemy_threat=0.8,
        enemy_count=2,
        distance_to_player=0.3,
        in_safe_area=False,
        heal_available=True
    )
    action = npc.update(state2)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Flee, "应该转换到Flee状态"
    
    print("\n3. 测试 Flee -> Heal 转换（到达安全区域且血量低）")
    state3 = WorldState(
        my_health=0.2,
        enemy_distance=0.95,
        enemy_threat=0.1,
        enemy_count=0,
        distance_to_player=0.5,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state3)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Heal, "应该转换到Heal状态"
    
    print("\n4. 测试 Heal -> Follow 转换（血量恢复，离玩家较远）")
    state4 = WorldState(
        my_health=0.75,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.8,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state4)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Follow, "应该转换到Follow状态"
    
    print("\n5. 测试 Follow -> Idle 转换（接近玩家）")
    state5 = WorldState(
        my_health=0.8,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.2,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state5)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Idle, "应该转换到Idle状态"
    
    print("\n6. 测试 Idle -> Heal 转换（血量低且在安全区域）")
    state6 = WorldState(
        my_health=0.4,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.3,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state6)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Heal, "应该转换到Heal状态"
    
    print("\n7. 测试 Heal -> Idle 转换（治疗完成）")
    state7 = WorldState(
        my_health=0.95,
        enemy_distance=1.0,
        enemy_threat=0.0,
        enemy_count=0,
        distance_to_player=0.3,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state7)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Idle, "应该转换到Idle状态"
    
    print("\n8. 测试 Attack -> Heal 转换（战斗中血量低但安全）")
    npc.current_state = FSMState.Attack
    state8 = WorldState(
        my_health=0.35,
        enemy_distance=0.7,
        enemy_threat=0.4,
        enemy_count=1,
        distance_to_player=0.3,
        in_safe_area=True,
        heal_available=True
    )
    action = npc.update(state8)
    print(f"   状态: {npc.get_current_state()}, 行为: {action}")
    assert npc.get_current_state() == FSMState.Heal, "应该转换到Heal状态"
    
    print("\n=== FSM与Utility AI的主要区别 ===")
    print("1. FSM使用硬编码的条件判断，有明确的转换优先级")
    print("2. Utility AI使用连续的评分函数，选择最高评分的行为")
    print("3. FSM的状态转换是离散的，容易预测和调试")
    print("4. Utility AI的行为选择更加平滑和灵活")
    print("5. FSM适合简单的、可预测的行为模式")
    print("6. Utility AI适合复杂的、需要权衡多个因素的场景")
    
    print("\n=== 所有测试通过 ===")


if __name__ == "__main__":
    test_fsm_npc()
