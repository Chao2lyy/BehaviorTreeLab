"""AI队友行为树交互式演示脚本

提供交互式菜单选择不同的战斗场景进行演示
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from ai_teammate import BattleSimulator


def main():
    print("选择要运行的场景:")
    print("1. 场景1: 基础战斗场景")
    print("2. 场景2: 紧急治疗场景")
    print("3. 场景3: 多个敌人场景")
    print("4. 运行所有场景")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        sim = BattleSimulator()
        sim.scenario_1_basic_combat()
    elif choice == "2":
        sim = BattleSimulator()
        sim.scenario_2_emergency_heal()
    elif choice == "3":
        sim = BattleSimulator()
        sim.scenario_3_multiple_enemies()
    elif choice == "4":
        sim1 = BattleSimulator()
        sim1.scenario_1_basic_combat()
        
        print("\n" + "="*60)
        print("按回车键继续下一个场景...")
        input()
        
        sim2 = BattleSimulator()
        sim2.scenario_2_emergency_heal()
        
        print("\n" + "="*60)
        print("按回车键继续下一个场景...")
        input()
        
        sim3 = BattleSimulator()
        sim3.scenario_3_multiple_enemies()
    else:
        print("无效选项，运行场景1作为默认")
        sim = BattleSimulator()
        sim.scenario_1_basic_combat()


if __name__ == "__main__":
    main()
