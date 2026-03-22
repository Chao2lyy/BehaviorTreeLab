# AI行为研究 - FSM vs 行为树 vs Utility AI

这是一个用于研究和对比三种不同AI决策系统的游戏演示项目。

## 项目概述

本项目实现了三种主流的AI决策系统，并在同一个游戏环境中进行对比：

1. **有限状态机(FSM)** - 硬编码状态转换，易于理解和调试
2. **行为树(Behavior Tree)** - 树状结构组织，模块化设计，易于扩展
3. **Utility AI** - 基于连续评分函数，平滑行为过渡，灵活权衡

## NPC行为列表

所有NPC支持以下行为：
- **Attack（攻击）** - 主动寻路接近并攻击最近的敌人
- **Heal（治疗）** - 原地治疗，恢复血量
- **Guard（警戒）** - 返回并守护自己的出生位置
- **Flee（逃跑）** - 逃离威胁源

## NPC行为特性

### FSM NPC (红色)
- **特点**：
  - 更早发现敌人就主动攻击
  - 低血量时仍坚持战斗
  - 更少倾向于治疗

### 行为树 NPC (蓝色)
- **特点**：
  - 更早治疗和逃跑
  - 需要更高威胁才会攻击
  - 优先级明确：逃跑 > 治疗 > 攻击 > 警戒

### Utility AI NPC (绿色)
- **特点**：
  - 平衡考虑所有因素（血量、威胁、安全等）
  - 根据评分最高选择行为
  - 平滑的行为过渡

## 运行方式

### GUI模式
```bash
python examples/ai_behavior_research/main.py
```

### 无头模式
```bash
python examples/ai_behavior_research/main.py --no-gui --frames 1000
```

### 命令行参数
- `--no-gui`: 使用无头模式运行（无图形界面）
- `--frames N`: 无头模式下运行N帧
- `--no-fps`: 不显示FPS信息
- `--target-fps N`: 设置目标FPS（默认60）


## 文件结构

```
examples/ai_behavior_research/
├── README.md            # 本文件
├── main.py              # 主入口文件
├── game.py              # 游戏主逻辑（含安全移动和障碍物避免）
├── gui.py               # 图形界面
├── config.py            # 配置文件
├── entities.py          # 实体定义
├── fsm_npc.py           # 有限状态机NPC
├── bt_npc.py            # 行为树NPC
├── utility_ai.py        # Utility AI
├── combat.py            # 战斗系统
├── movement.py          # 移动系统（含安全位置跟踪）
├── pathfinding.py       # 寻路系统（A*算法）
├── grid_map.py          # 网格地图
└── test_pathfinding.py  # 寻路测试
```

## 系统要求

- Python 3.7+
- Pygame 2.0+

## 安装依赖

```bash
pip install pygame
```

## 三种AI决策系统对比

| 特性 | FSM | 行为树 | Utility AI |
|------|-----|--------|------------|
| 可预测性 | 高 | 中 | 低 |
| 可扩展性 | 中 | 高 | 高 |
| 调试难度 | 低 | 中 | 高 |
| 行为平滑度 | 低 | 中 | 高 |
| 实现复杂度 | 低 | 中 | 高 |
| 适合场景 | 简单行为 | 复杂行为 | 需要权衡的场景 |
