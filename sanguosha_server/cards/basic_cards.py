"""
卡牌基类和基本卡牌类型
"""
class Card:
    def __init__(self, name, suit, point, description=""):
        self.name = name
        self.suit = suit  # 花色：黑桃、红心、梅花、方块
        self.point = point  # 点数：A-2-K
        self.description = description
        self.type = "basic"  # basic, trick, equipment
        
    def play(self, game, player, target=None):
        """出牌效果"""
        raise NotImplementedError("每张卡牌都需要实现play方法")

# 基本牌
class BasicCard(Card):
    pass

class Sha(BasicCard):
    def __init__(self):
        super().__init__("杀", "", 0, "对一名其他角色使用，若其未使用【闪】抵消，则对其造成1点伤害")
        
    def play(self, game, player, target=None):
        # 【杀】的效果实现
        print(f"{player.name} 对 {target.name} 使用了 【杀】")
        return True

class Shan(BasicCard):
    def __init__(self):
        super().__init__("闪", "", 0, "用于抵消【杀】")
        
    def play(self, game, player, target=None):
        # 【闪】的效果实现
        print(f"{player.name} 使用了 【闪】 抵消了攻击")
        return True

class Tao(BasicCard):
    def __init__(self):
        super().__init__("桃", "", 0, "回复1点体力")
        
    def play(self, game, player, target=None):
        # 【桃】的效果实现
        target = target or player
        if target.hp < target.max_hp:
            target.hp += 1
            print(f"{target.name} 使用了 【桃】，回复了1点体力")
        else:
            print(f"{target.name} 体力已满，不能使用 【桃】")
        return True