"""
三国杀游戏入口
"""
from game import SanGuoShaGame
from game.player import Player
from characters import ExampleCharacter
from cards.basic_cards import Sha, Shan, Tao

def main():
    print("欢迎来到三国杀！")
    
    # 创建游戏实例
    game = SanGuoShaGame()
    
    # 添加玩家
    player1 = Player("玩家1")
    player1.character = ExampleCharacter()  # 分配一个示例武将
    player1.hp = player1.character.hp
    player1.max_hp = player1.character.max_hp
    
    player2 = Player("玩家2")
    player2.character = ExampleCharacter()  # 分配一个示例武将
    player2.hp = player2.character.hp
    player2.max_hp = player2.character.max_hp
    
    game.add_player(player1)
    game.add_player(player2)
    
    # 给玩家发牌（示例）
    player1.hand_cards = [Sha(), Tao(), Shan()]
    player2.hand_cards = [Sha(), Sha(), Tao()]
    
    # 开始游戏
    game.start_game()
    
    # 显示初始状态
    from ui.console_ui import display_game_state, display_hand_cards
    display_game_state(game)
    display_hand_cards(player1)
    
    print("\n游戏初始化完成！接下来可以实现更详细的回合流程。")

if __name__ == "__main__":
    main()