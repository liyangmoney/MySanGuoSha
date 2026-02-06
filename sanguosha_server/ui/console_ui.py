"""
简单命令行界面
"""
def display_game_state(game):
    """显示游戏状态"""
    print("\n=== 当前游戏状态 ===")
    for i, player in enumerate(game.players):
        print(f"{i+1}. {player.name} - 角色:{player.character.name if player.character else '未选择'} - HP:{player.hp}/{player.max_hp} - 身份:{player.identity}")

def display_hand_cards(player):
    """显示玩家手牌"""
    print(f"\n{player.name} 的手牌:")
    for i, card in enumerate(player.hand_cards):
        print(f"{i+1}. {card.name}")

def get_user_input(prompt):
    """获取用户输入"""
    return input(prompt)