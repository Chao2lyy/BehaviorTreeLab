from typing import Callable, Optional
from .node import Node
from .types import NodeStatus


class Action(Node):
    """动作节点
    
    执行具体动作的叶子节点，通过回调函数实现
    """
    
    def __init__(self, callback: Callable[[], NodeStatus], name: Optional[str] = None):
        """初始化动作节点
        
        Args:
            callback: 动作执行回调函数，返回NodeStatus
            name: 节点名称
        """
        super().__init__(name)
        self.callback = callback  # 动作回调函数

    def tick(self) -> NodeStatus:
        """执行动作
        
        Returns:
            回调函数返回的状态
        """
        return self.callback()


class Condition(Node):
    """条件节点
    
    检查条件的叶子节点，通过回调函数实现
    """
    
    def __init__(self, callback: Callable[[], bool], name: Optional[str] = None):
        """初始化条件节点
        
        Args:
            callback: 条件检查回调函数，返回bool
            name: 节点名称
        """
        super().__init__(name)
        self.callback = callback  # 条件回调函数

    def tick(self) -> NodeStatus:
        """检查条件
        
        Returns:
            条件为True返回SUCCESS，否则返回FAILURE
        """
        if self.callback():
            return NodeStatus.SUCCESS
        return NodeStatus.FAILURE
