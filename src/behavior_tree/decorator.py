from typing import Optional
from .node import Node
from .types import NodeStatus


class Decorator(Node):
    """装饰节点基类
    
    包装单个子节点的节点基类
    """
    
    def __init__(self, child: Optional[Node] = None, name: Optional[str] = None):
        """初始化装饰节点
        
        Args:
            child: 被包装的子节点
            name: 节点名称
        """
        super().__init__(name)
        self.child = child  # 被装饰的子节点

    @property
    def blackboard(self):
        """获取黑板"""
        return super().blackboard

    @blackboard.setter
    def blackboard(self, value):
        """设置黑板，同时设置子节点的黑板"""
        self._blackboard = value
        if self.child:
            self.child.blackboard = value

    def reset(self):
        """重置节点，同时重置子节点"""
        if self.child:
            self.child.reset()


class Inverter(Decorator):
    """取反节点
    
    取反子节点的返回状态：
    - SUCCESS -> FAILURE
    - FAILURE -> SUCCESS
    - RUNNING -> RUNNING
    """
    
    def tick(self) -> NodeStatus:
        """执行取反逻辑
        
        Returns:
            取反后的节点状态
        """
        if not self.child:
            return NodeStatus.FAILURE
        
        status = self.child.tick()
        
        if status == NodeStatus.SUCCESS:
            return NodeStatus.FAILURE
        elif status == NodeStatus.FAILURE:
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.RUNNING


class Repeater(Decorator):
    """重复节点
    
    重复执行子节点N次
    
    times=-1表示无限重复
    """
    
    def __init__(self, child: Optional[Node] = None, 
                 times: int = -1, name: Optional[str] = None):
        """初始化重复节点
        
        Args:
            child: 被装饰的子节点
            times: 重复次数，-1表示无限
            name: 节点名称
        """
        super().__init__(child, name)
        self.times = times  # 重复次数
        self._current = 0  # 当前重复次数

    def tick(self) -> NodeStatus:
        """执行重复逻辑
        
        Returns:
            节点执行状态
        """
        if not self.child:
            return NodeStatus.FAILURE
        
        while self.times == -1 or self._current < self.times:
            status = self.child.tick()
            
            if status == NodeStatus.RUNNING:
                # 子节点正在执行，保持当前状态
                return NodeStatus.RUNNING
            elif status == NodeStatus.FAILURE:
                # 子节点失败，重置计数并返回失败
                self._current = 0
                return NodeStatus.FAILURE
            
            # 子节点成功，继续下一次
            self._current += 1
            self.child.reset()
        
        # 完成所有重复，重置计数并返回成功
        self._current = 0
        return NodeStatus.SUCCESS

    def reset(self):
        """重置节点，重置当前次数和子节点"""
        super().reset()
        self._current = 0


class UntilFail(Decorator):
    """直到失败节点
    
    持续执行子节点直到失败
    子节点失败后返回SUCCESS
    """
    
    def tick(self) -> NodeStatus:
        """执行直到失败逻辑
        
        Returns:
            节点执行状态
        """
        if not self.child:
            return NodeStatus.FAILURE
        
        while True:
            status = self.child.tick()
            
            if status == NodeStatus.RUNNING:
                # 子节点正在执行，保持当前状态
                return NodeStatus.RUNNING
            elif status == NodeStatus.FAILURE:
                # 子节点失败，重置并返回成功
                self.child.reset()
                return NodeStatus.SUCCESS
            
            # 子节点成功，继续执行
            self.child.reset()
