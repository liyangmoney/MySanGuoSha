"""
三国杀游戏主控制器
"""
class SanGuoShaGame:
    def __init__(self):
        self.players = []
        self.current_player = None
        self.game_state = "waiting_for_players"
        self.deck = []
        
    def add_player(self, player):
        """添加玩家"""
        self.players.append(player)
        
    def start_game(self):
        """开始游戏"""
        if len(self.players) >= 2:
            self.game_state = "running"
            # 初始化游戏逻辑
            print("游戏开始！")
        else:
            print("玩家数量不足，无法开始游戏")
            
    def next_turn(self):
        """切换到下一个玩家回合"""
        pass
        
    def check_victory(self):
        """检查胜利条件"""
        pass