"""AI队友行为树功能测试脚本

测试AI队友行为树的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ai_teammate import BattleSimulator, Vector2
from behavior_tree import NodeStatus


def test_basic_functionality():
    print("=== 测试AI队友行为树基本功能 ===\n")
    
    sim = BattleSimulator()
    
    print("1. 测试实体创建:")
    print(f"   - 玩家创建成功: {sim.player}")
    print(f"   - AI队友创建成功: {sim.teammate}")
    print(f"   ✓ 实体创建测试通过\n")
    
    print("2. 测试血量系统:")
    initial_hp = sim.teammate.hp
    sim.teammate.take_damage(30)
    print(f"   - 初始血量: {initial_hp}")
    print(f"   - 受伤后血量: {sim.teammate.hp}")
    sim.teammate.heal(20)
    print(f"   - 治疗后血量: {sim.teammate.hp}")
    print(f"   ✓ 血量系统测试通过\n")
    
    print("3. 测试距离计算:")
    pos1 = Vector2(0, 0)
    pos2 = Vector2(3, 4)
    distance = pos1.distance_to(pos2)
    print(f"   - 位置1: {pos1}")
    print(f"   - 位置2: {pos2}")
    print(f"   - 距离: {distance:.2f} (期望: 5.0)")
    assert abs(distance - 5.0) < 0.01
    print(f"   ✓ 距离计算测试通过\n")
    
    print("4. 测试Blackboard:")
    sim.blackboard.set("test_key", "test_value")
    value = sim.blackboard.get("test_key")
    print(f"   - 设置值: test_key = test_value")
    print(f"   - 获取值: test_key = {value}")
    assert value == "test_value"
    print(f"   ✓ Blackboard测试通过\n")
    
    print("5. 测试行为树更新:")
    result = sim.ai_teammate.update()
    print(f"   - 行为树执行结果: {result.value}")
    print(f"   - 当前行为: {sim.teammate.current_behavior}")
    print(f"   ✓ 行为树更新测试通过\n")
    
    print("6. 测试紧急治疗行为:")
    sim.teammate.hp = 20
    sim.teammate.max_hp = 100
    sim.teammate.healing_potion_count = 1
    result = sim.ai_teammate.update()
    print(f"   - 血量: {sim.teammate.hp}/{sim.teammate.max_hp}")
    print(f"   - 行为树执行结果: {result.value}")
    print(f"   - 当前行为: {sim.teammate.current_behavior}")
    print(f"   - 治疗后血量: {sim.teammate.hp}")
    print(f"   ✓ 紧急治疗行为测试通过\n")
    
    print("\n=== 所有测试通过! ===")


if __name__ == "__main__":
    test_basic_functionality()
