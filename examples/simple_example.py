import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from behavior_tree import (
    NodeStatus,
    Blackboard,
    Action,
    Condition,
    Sequence,
    Selector,
    Inverter,
    Repeater,
)


def main():
    print("=== 行为树框架使用示例 ===\n")
    
    # 示例1: 简单的Sequence节点
    print("示例1: Sequence节点 - 依次执行所有任务")
    seq = Sequence([
        Action(lambda: (print("  任务1: 起床"), NodeStatus.SUCCESS)[1]),
        Action(lambda: (print("  任务2: 刷牙"), NodeStatus.SUCCESS)[1]),
        Action(lambda: (print("  任务3: 吃早餐"), NodeStatus.SUCCESS)[1]),
    ])
    result = seq.tick()
    print(f"结果: {result.value}\n")
    
    # 示例2: Selector节点 - 选择第一个成功的任务
    print("示例2: Selector节点 - 选择第一个成功的任务")
    sel = Selector([
        Action(lambda: (print("  尝试: 走路去上班"), NodeStatus.FAILURE)[1]),
        Action(lambda: (print("  尝试: 坐公交去上班"), NodeStatus.SUCCESS)[1]),
        Action(lambda: (print("  尝试: 打车去上班"), NodeStatus.SUCCESS)[1]),
    ])
    result = sel.tick()
    print(f"结果: {result.value}\n")
    
    # 示例3: 使用Blackboard共享数据
    print("示例3: 使用Blackboard共享数据")
    bb = Blackboard()
    
    def set_player_hp():
        bb.set("player_hp", 100)
        print(f"  设置玩家血量: {bb.get('player_hp')}")
        return NodeStatus.SUCCESS
    
    def check_low_hp():
        hp = bb.get("player_hp", 0)
        print(f"  检查玩家血量: {hp}")
        return hp < 50
    
    def heal_player():
        hp = bb.get("player_hp", 0)
        bb.set("player_hp", hp + 50)
        print(f"  治疗玩家! 血量: {bb.get('player_hp')}")
        return NodeStatus.SUCCESS
    
    behavior_tree = Sequence([
        Action(set_player_hp),
        Selector([
            Inverter(Condition(check_low_hp)),
            Action(heal_player),
        ]),
    ])
    behavior_tree.blackboard = bb
    
    result = behavior_tree.tick()
    print(f"结果: {result.value}\n")
    
    # 示例4: Repeater节点 - 重复执行
    print("示例4: Repeater节点 - 重复执行3次")
    count = 0
    def count_action():
        nonlocal count
        count += 1
        print(f"  计数: {count}")
        return NodeStatus.SUCCESS
    
    rep = Repeater(Action(count_action), times=3)
    result = rep.tick()
    print(f"结果: {result.value}\n")


if __name__ == "__main__":
    main()
