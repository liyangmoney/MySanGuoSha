"""
玩家类定义
"""
class Player:
    def __init__(self, name, identity=None, character=None):
        self.name = name
        self.identity = identity  # 主公、忠臣、反贼、内奸
        self.character = character  # 武将
        self.hand_cards = []  # 手牌
        self.hp = 0  # 生命值
        self.max_hp = 0  # 最大生命值
        self.is_alive = True
        
    def draw_card(self, num=1):
        """抽牌"""
        pass
        
    def play_card(self, card):
        """出牌"""
        pass
        
    def use_skill(self, skill):
        """使用技能"""
        pass