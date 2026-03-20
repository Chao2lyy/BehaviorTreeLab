from typing import Any, Optional


class Blackboard:
    """黑板类
    
    用于在行为树节点之间共享数据的黑板类
    支持父子黑板继承关系
    """
    
    def __init__(self, parent: Optional['Blackboard'] = None):
        """初始化黑板
        
        Args:
            parent: 父黑板，用于实现数据继承
        """
        self._data: dict[str, Any] = {}  # 存储数据的字典
        self._parent = parent  # 父黑板引用

    def get(self, key: str, default: Any = None) -> Any:
        """获取数据
        
        先从当前黑板查找，找不到则从父黑板查找
        
        Args:
            key: 数据键名
            default: 默认值
            
        Returns:
            找到的数据或默认值
        """
        if key in self._data:
            return self._data[key]
        if self._parent:
            return self._parent.get(key, default)
        return default

    def set(self, key: str, value: Any) -> None:
        """设置数据
        
        Args:
            key: 数据键名
            value: 数据值
        """
        self._data[key] = value

    def has(self, key: str) -> bool:
        """检查是否包含指定键
        
        Args:
            key: 数据键名
            
        Returns:
            是否包含该键
        """
        if key in self._data:
            return True
        if self._parent:
            return self._parent.has(key)
        return False

    def delete(self, key: str) -> bool:
        """删除数据
        
        Args:
            key: 数据键名
            
        Returns:
            是否成功删除
        """
        if key in self._data:
            del self._data[key]
            return True
        return False

    def clear(self) -> None:
        """清空当前黑板的所有数据"""
        self._data.clear()

    def __getitem__(self, key: str) -> Any:
        """字典式获取数据"""
        return self.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        """字典式设置数据"""
        self.set(key, value)

    def __contains__(self, key: str) -> bool:
        """in运算符支持"""
        return self.has(key)
