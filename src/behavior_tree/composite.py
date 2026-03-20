from typing import List, Optional
from enum import Enum
from .node import Node
from .types import NodeStatus


class ParallelPolicy(Enum):
    """并行节点执行策略
    
    定义Parallel节点如何判断成功或失败
    """
    REQUIRE_ONE = "require_one"  # 任一子节点成功即成功
    REQUIRE_ALL = "require_all"   # 所有子节点都成功才成功


class Composite(Node):
    """组合节点基类
    
    可以包含多个子节点的节点基类
    """
    
    def __init__(self, children: Optional[List[Node]] = None, name: Optional[str] = None):

        """初始化组合节点
        
        Args:
            children: 子节点列表
            name: 节点名称
        """
        super().__init__(name)
        self.children: List[Node] = children or []  # 子节点列表

    def add_child(self, child: Node) -> 'Composite':
        """添加子节点
        
        Args:
            child: 要添加的子节点
            
        Returns:
            self，支持链式调用
        """
        self.children.append(child)
        return self

    def remove_child(self, child: Node) -> 'Composite':
        """移除子节点
        
        Args:
            child: 要移除的子节点
            
        Returns:
            self，支持链式调用
        """
        if child in self.children:
            self.children.remove(child)
        return self

    @property
    def blackboard(self):
        """获取黑板"""
        return super().blackboard

    @blackboard.setter
    def blackboard(self, value):
        """设置黑板，同时设置所有子节点的黑板"""
        self._blackboard = value
        for child in self.children:
            child.blackboard = value

    def reset(self):
        """重置节点，同时重置所有子节点"""
        for child in self.children:
            child.reset()


class Sequence(Composite):
    """顺序节点
    
    依次执行子节点，全部成功才返回成功，任一失败则返回失败
    """
    
    def __init__(self, children: Optional[List[Node]] = None, name: Optional[str] = None):
        """初始化顺序节点
        
        Args:
            children: 子节点列表
            name: 节点名称
        """
        super().__init__(children, name)
        self._current_index = 0  # 当前执行到的子节点索引

    def tick(self) -> NodeStatus:
        """执行顺序节点逻辑
        
        Returns:
            节点执行状态
        """
        while self._current_index < len(self.children):
            child = self.children[self._current_index]
            status = child.tick()
            
            if status == NodeStatus.RUNNING:
                # 子节点正在执行，保持当前状态
                return NodeStatus.RUNNING
            elif status == NodeStatus.FAILURE:
                # 子节点失败，重置索引并返回失败
                self._current_index = 0
                return NodeStatus.FAILURE
            
            # 子节点成功，继续下一个
            self._current_index += 1
        
        # 所有子节点都成功，重置索引并返回成功
        self._current_index = 0
        return NodeStatus.SUCCESS

    def reset(self):
        """重置节点，重置当前索引和所有子节点"""
        super().reset()
        self._current_index = 0


class Selector(Composite):
    """选择节点
    
    依次执行子节点，任一成功则返回成功，全部失败才返回失败
    """
    
    def __init__(self, children: Optional[List[Node]] = None, name: Optional[str] = None):
        """初始化选择节点
        
        Args:
            children: 子节点列表
            name: 节点名称
        """
        super().__init__(children, name)
        self._current_index = 0  # 当前执行到的子节点索引

    def tick(self) -> NodeStatus:
        """执行选择节点逻辑
        
        Returns:
            节点执行状态
        """
        while self._current_index < len(self.children):
            child = self.children[self._current_index]
            status = child.tick()
            
            if status == NodeStatus.RUNNING:
                # 子节点正在执行，保持当前状态
                return NodeStatus.RUNNING
            elif status == NodeStatus.SUCCESS:
                # 子节点成功，重置索引并返回成功
                self._current_index = 0
                return NodeStatus.SUCCESS
            
            # 子节点失败，继续下一个
            self._current_index += 1
        
        # 所有子节点都失败，重置索引并返回失败
        self._current_index = 0
        return NodeStatus.FAILURE

    def reset(self):
        """重置节点，重置当前索引和所有子节点"""
        super().reset()
        self._current_index = 0


class Parallel(Composite):
    """并行节点
    
    同时执行所有子节点，根据策略判断成功或失败
    """
    
    def __init__(self, children: Optional[List[Node]] = None, 
                 policy: ParallelPolicy = ParallelPolicy.REQUIRE_ALL,
                 name: Optional[str] = None):
        """初始化并行节点
        
        Args:
            children: 子节点列表
            policy: 并行策略
            name: 节点名称
        """
        super().__init__(children, name)
        self.policy = policy  # 并行执行策略

    def tick(self) -> NodeStatus:
        """执行并行节点逻辑
        
        Returns:
            节点执行状态
        """
        success_count = 0  # 成功的子节点数
        failure_count = 0  # 失败的子节点数
        
        # 执行所有子节点
        for child in self.children:
            status = child.tick()
            
            if status == NodeStatus.RUNNING:
                # 子节点正在执行，继续执行其他子节点
                continue
            elif status == NodeStatus.SUCCESS:
                success_count += 1
            else:
                failure_count += 1
        
        # 根据策略判断结果
        if self.policy == ParallelPolicy.REQUIRE_ONE:
            # 任一成功即可
            if success_count > 0:
                self.reset()
                return NodeStatus.SUCCESS
            if failure_count == len(self.children):
                self.reset()
                return NodeStatus.FAILURE
        else:
            # 全部成功才可
            if success_count == len(self.children):
                self.reset()
                return NodeStatus.SUCCESS
            if failure_count > 0:
                self.reset()
                return NodeStatus.FAILURE
        
        # 还有子节点在执行
        return NodeStatus.RUNNING
