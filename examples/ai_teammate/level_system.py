class LevelSystem:
    """等级系统"""
    
    def __init__(self, config):
        self.config = config
        self.level = 1
        self.experience = 0
        self.experience_to_next = config.base_experience
    
    def add_experience(self, amount: int):
        """增加经验"""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self.experience -= self.experience_to_next
            self.level_up()
    
    def level_up(self):
        """升级"""
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * self.config.experience_multiplier)
