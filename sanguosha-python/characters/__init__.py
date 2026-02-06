"""
武将类定义
"""
class Character:
    def __init__(self, name, hp, skills=None, gender="male", camp="wei"):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.skills = skills or []
        self.gender = gender
        self.camp = camp  # 阵营：魏蜀吴群
        
    def use_skill(self, skill_name, game, player, target=None):
        """使用技能"""
        for skill in self.skills:
            if skill.name == skill_name:
                return skill.activate(game, player, target)
        return False

class Skill:
    def __init__(self, name, description, activation_condition="manual"):
        self.name = name
        self.description = description
        self.activation_condition = activation_condition  # manual, auto, trigger
        
    def activate(self, game, player, target=None):
        """激活技能"""
        raise NotImplementedError("每个技能都需要实现activate方法")

# 示例武将
class ExampleCharacter(Character):
    def __init__(self):
        skills = [
            Skill("example_skill", "示例技能效果", "manual")
        ]
        super().__init__("示例武将", 3, skills)