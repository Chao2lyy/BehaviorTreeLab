from abc import ABC, abstractmethod
from typing import Optional
from .types import NodeStatus
from .blackboard import Blackboard


class Node(ABC):
    """行为树节点基类
    
    所有行为树节点的抽象基类，定义了节点的基本接口
    """
    
    def __init__(self, name: Optional[str] = None):
        """初始化节点
        
        Args:
            name: 节点名称，默认为类名
        """
        self.name = name or self.__class__.__name__  # 节点名称
        self._blackboard: Optional[Blackboard] = None  # 黑板引用

    @property
    def blackboard(self) -> Optional[Blackboard]:
        """获取节点的黑板"""
        return self._blackboard

    @blackboard.setter
    def blackboard(self, value: Blackboard) -> None:
        """设置节点的黑板"""
        self._blackboard = value

    @abstractmethod
    def tick(self) -> NodeStatus:
        """执行节点逻辑
        
        Returns:
            节点执行后的状态
        """
        pass

    def reset(self) -> None:
        """重置节点状态
        
        用于重置节点到初始状态，子类可根据需要重写
        """
        pass
