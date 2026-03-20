from enum import Enum


class NodeStatus(Enum):
    """节点状态枚举
    
    定义行为树节点执行后的返回状态
    """
    SUCCESS = "success"    # 节点执行成功
    FAILURE = "failure"    # 节点执行失败
    RUNNING = "running"    # 节点正在执行中
