"""分数管理器"""

import json
import os
from typing import List, Dict
from datetime import datetime


class ScoreEntry:
    """分数条目"""
    
    def __init__(self, score: int, timestamp: str = None):
        self.score = score
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self) -> Dict:
        return {
            "score": self.score,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScoreEntry':
        return cls(data["score"], data["timestamp"])


class ScoreManager:
    """分数管理器"""
    
    def __init__(self, config):
        """初始化分数管理器
        
        Args:
            config: 游戏配置对象
        """
        self.config = config
        self.current_score = 0
        self.score_history: List[ScoreEntry] = []
        self.scores_file = os.path.join(os.path.dirname(__file__), "..", "scores.json")
        self.load_scores()
    
    def add_score(self, points: int):
        """增加分数
        
        Args:
            points: 要增加的分数
        """
        self.current_score += points
    
    def reset_current_score(self):
        """重置当前分数"""
        self.current_score = 0
    
    def save_score(self):
        """保存当前分数到历史记录"""
        if self.current_score > 0:
            entry = ScoreEntry(self.current_score)
            self.score_history.append(entry)
            self.score_history.sort(key=lambda x: x.score, reverse=True)
            self.score_history = self.score_history[:self.config.score.max_score_history]
            self._save_to_file()
    
    def load_scores(self):
        """从文件加载分数历史"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.score_history = [ScoreEntry.from_dict(entry) for entry in data]
        except Exception as e:
            print(f"加载分数失败: {e}")
            self.score_history = []
    
    def _save_to_file(self):
        """保存到文件"""
        try:
            data = [entry.to_dict() for entry in self.score_history]
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存分数失败: {e}")
    
    def get_top_scores(self, count: int = 10) -> List[ScoreEntry]:
        """获取最高分数
        
        Args:
            count: 要获取的分数数量
            
        Returns:
            最高分数列表
        """
        return self.score_history[:count]
