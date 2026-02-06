"""
三国杀服务器 - 完整游戏逻辑
"""
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import random
import copy

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'sanguosha_secret_key'

# 配置SocketIO以兼容云环境
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=True, 
    engineio_logger=True,
    cors_credentials=True,
    ping_timeout=60,
    ping_interval=25
)

# 卡牌定义
CARDS = [
    # 基本牌
    {'name': '杀', 'type': 'basic', 'suit': 'heart', 'point': 1},
    {'name': '杀', 'type': 'basic', 'suit': 'diamond', 'point': 2},
    {'name': '杀', 'type': 'basic', 'suit': 'spade', 'point': 1},
    {'name': '杀', 'type': 'basic', 'suit': 'club', 'point': 1},
    {'name': '闪', 'type': 'basic', 'suit': 'heart', 'point': 2},
    {'name': '闪', 'type': 'basic', 'suit': 'diamond', 'point': 2},
    {'name': '桃', 'type': 'basic', 'suit': 'heart', 'point': 3},
    {'name': '桃', 'type': 'basic', 'suit': 'spade', 'point': 3},
]

# 武将定义
CHARACTERS = [
    {'name': '刘备', 'hp': 4, 'skills': ['仁德']},
    {'name': '关羽', 'hp': 4, 'skills': ['武圣']},
    {'name': '张飞', 'hp': 4, 'skills': ['咆哮']},
    {'name': '诸葛亮', 'hp': 3, 'skills': ['观星', '空城']},
    {'name': '赵云', 'hp': 4, 'skills': ['龙胆']},
    {'name': '马超', 'hp': 4, 'skills': ['铁骑']},
    {'name': '黄月英', 'hp': 3, 'skills': ['集智', '奇才']},
    {'name': '曹操', 'hp': 4, 'skills': ['奸雄', '护驾']},
    {'name': '司马懿', 'hp': 3, 'skills': ['反馈', '鬼才']},
    {'name': '夏侯惇', 'hp': 4, 'skills': ['刚烈']},
]

# 游戏房间存储
rooms = {}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@app.route('/api/create_room', methods=['POST'])
def create_room():
    """创建游戏房间"""
    try:
        data = request.json
        room_id = str(uuid.uuid4())
        max_players = data.get('max_players', 2)
        
        rooms[room_id] = {
            'id': room_id,
            'players': [],
            'max_players': max_players,
            'status': 'waiting'  # waiting, running, finished
        }
        
        return jsonify({
            'success': True,
            'room_id': room_id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def initialize_game(room_id):
    """初始化游戏状态"""
    room = rooms[room_id]
    
    # 生成卡牌堆
    deck = copy.deepcopy(CARDS) * 3  # 使用多副牌
    random.shuffle(deck)
    
    # 为每个玩家分配武将
    available_characters = copy.deepcopy(CHARACTERS)
    random.shuffle(available_characters)
    
    for i, player in enumerate(room['players']):
        # 分配武将
        if i < len(available_characters):
            char = available_characters[i]
            player['character'] = char['name']
            player['max_hp'] = char['hp']
            player['hp'] = char['hp']
            player['skills'] = char['skills']
        else:
            # 如果武将不够，使用默认武将
            player['character'] = "普通武将"
            player['max_hp'] = 4
            player['hp'] = 4
            player['skills'] = []
        
        # 分配初始手牌（3张）
        player['hand_cards'] = []
        for _ in range(4):  # 每人4张起始手牌
            if deck:
                player['hand_cards'].append(deck.pop())
    
    # 设置游戏状态
    room['deck'] = deck
    room['current_player_index'] = 0
    room['game_phase'] = 'start_turn'  # start_turn, draw_phase, play_phase, discard_phase
    room['round'] = 1
    room['alive_players'] = [p['name'] for p in room['players']]
    room['last_action'] = None
    room['target'] = None

@app.route('/api/join_room/<room_id>', methods=['POST'])
def join_room_api(room_id):
    """加入游戏房间"""
    try:
        if room_id not in rooms:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        room = rooms[room_id]
        if room['status'] != 'waiting':
            return jsonify({'success': False, 'error': '房间已经开始游戏'})
        
        if len(room['players']) >= room['max_players']:
            return jsonify({'success': False, 'error': '房间人数已满'})
        
        player_name = request.json.get('player_name')
        if not player_name:
            return jsonify({'success': False, 'error': '玩家名称不能为空'})
        
        # 检查玩家名称是否已存在
        for player in room['players']:
            if player['name'] == player_name:
                return jsonify({'success': False, 'error': '该玩家名称已被使用'})
        
        # 创建玩家数据
        player_data = {
            'name': player_name,
            'id': len(room['players']),
            'hp': 3,
            'max_hp': 3,
            'character': '示例武将',
            'hand_cards': [],
            'equipped_cards': [],  # 装备区
            'is_alive': True
        }
        
        room['players'].append(player_data)
        
        # 通知房间内所有玩家有新玩家加入
        socketio.emit('player_joined', {
            'player_name': player_name,
            'players': [p['name'] for p in room['players']],
            'room_id': room_id
        }, room=room_id)
        
        # 如果达到最大玩家数，自动开始游戏
        if len(room['players']) == room['max_players']:
            room['status'] = 'running'
            initialize_game(room_id)  # 初始化游戏
            socketio.emit('game_start', {
                'players': [{
                    'name': p['name'],
                    'character': p['character'], 
                    'hp': p['hp'],
                    'max_hp': p['max_hp'],
                    'hand_card_count': len(p['hand_cards'])
                } for p in room['players']], 
                'room_id': room_id,
                'current_player': room['players'][room['current_player_index']]['name']
            }, room=room_id)
        
        return jsonify({
            'success': True,
            'player_id': len(room['players']) - 1,
            'room_info': {
                'room_id': room_id,
                'players': [p['name'] for p in room['players']],
                'max_players': room['max_players'],
                'status': room['status']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/rooms/<room_id>')
def get_room_info(room_id):
    """获取房间信息"""
    try:
        if room_id not in rooms:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        room = rooms[room_id]
        return jsonify({
            'success': True,
            'room_info': {
                'room_id': room_id,
                'players': [p['name'] for p in room['players']],
                'max_players': room['max_players'],
                'status': room['status'],
                'game_phase': room.get('game_phase', 'waiting'),
                'current_player': room.get('players', [])[room.get('current_player_index', 0)]['name'] if room.get('players') and room.get('current_player_index') is not None else None,
                'round': room.get('round', 1)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/game/action', methods=['POST'])
def game_action():
    """处理游戏动作"""
    try:
        data = request.json
        room_id = data.get('room_id')
        action = data.get('action')  # 'play_card', 'use_skill', 'discard', 'draw'
        player_name = data.get('player_name')
        target = data.get('target')
        card = data.get('card')
        
        if room_id not in rooms:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        room = rooms[room_id]
        if room['status'] != 'running':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        # 找到当前玩家
        player = None
        player_index = None
        for i, p in enumerate(room['players']):
            if p['name'] == player_name:
                player = p
                player_index = i
                break
        
        if not player:
            return jsonify({'success': False, 'error': '玩家不存在'})
        
        if player_index != room['current_player_index']:
            return jsonify({'success': False, 'error': '不是你的回合'})
        
        result = {'success': True, 'message': ''}
        
        if action == 'play_card':
            # 检查玩家是否持有该卡牌
            if card not in player['hand_cards']:
                return jsonify({'success': False, 'error': '玩家没有这张牌'})
            
            # 执行卡牌效果
            if card['name'] == '杀':
                # 检查目标
                if not target:
                    return jsonify({'success': False, 'error': '请选择目标'})
                
                # 检查目标是否有效
                target_player = None
                for p in room['players']:
                    if p['name'] == target and p['is_alive']:
                        target_player = p
                        break
                
                if not target_player:
                    return jsonify({'success': False, 'error': '无效的目标'})
                
                # 从手牌中移除卡牌
                player['hand_cards'].remove(card)
                
                # 广播出牌消息
                socketio.emit('card_played', {
                    'player': player_name,
                    'card': card,
                    'target': target,
                    'action': 'attack'
                }, room=room_id)
                
                result['message'] = f'{player_name} 对 {target} 使用了【杀】'
                
            elif card['name'] == '闪':
                # 闪是用来响应杀的
                if not room.get('last_action') or room['last_action']['action'] != 'attack':
                    return jsonify({'success': False, 'error': '不能响应当前动作'})
                
                # 从手牌中移除卡牌
                player['hand_cards'].remove(card)
                
                socketio.emit('card_played', {
                    'player': player_name,
                    'card': card,
                    'action': 'dodge'
                }, room=room_id)
                
                result['message'] = f'{player_name} 使用了【闪】'
                
            elif card['name'] == '桃':
                # 桃用于恢复体力
                if player['hp'] >= player['max_hp']:
                    return jsonify({'success': False, 'error': '体力已满，不能使用桃'})
                
                player['hp'] += 1
                player['hand_cards'].remove(card)
                
                socketio.emit('card_played', {
                    'player': player_name,
                    'card': card,
                    'action': 'peach',
                    'new_hp': player['hp']
                }, room=room_id)
                
                result['message'] = f'{player_name} 使用了【桃】，体力恢复至 {player["hp"]}'
        
        elif action == 'draw_card':
            # 摸牌阶段 - 摸两张牌
            drawn_cards = []
            for _ in range(2):
                if room['deck']:
                    drawn_cards.append(room['deck'].pop())
            
            player['hand_cards'].extend(drawn_cards)
            
            socketio.emit('card_drawn', {
                'player': player_name,
                'count': len(drawn_cards),
                'hand_card_count': len(player['hand_cards'])
            }, room=room_id)
            
            result['message'] = f'{player_name} 摸了 {len(drawn_cards)} 张牌'
        
        elif action == 'end_turn':
            # 结束当前回合，轮到下一位玩家
            room['current_player_index'] = (room['current_player_index'] + 1) % len(room['players'])
            next_player = room['players'][room['current_player_index']]
            
            socketio.emit('turn_changed', {
                'current_player': next_player['name'],
                'round': room['round']
            }, room=room_id)
            
            result['message'] = f'回合切换到 {next_player["name"]}'
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/game/state/<room_id>')
def get_game_state(room_id):
    """获取游戏状态"""
    try:
        if room_id not in rooms:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        room = rooms[room_id]
        if room['status'] != 'running':
            return jsonify({'success': False, 'error': '游戏未开始'})
        
        game_state = {
            'room_id': room_id,
            'status': room['status'],
            'game_phase': room.get('game_phase', 'waiting'),
            'current_player': room['players'][room['current_player_index']]['name'],
            'round': room['round'],
            'players': []
        }
        
        for player in room['players']:
            player_info = {
                'name': player['name'],
                'character': player['character'],
                'hp': player['hp'],
                'max_hp': player['max_hp'],
                'is_alive': player['is_alive'],
                'hand_card_count': len(player['hand_cards']) if player['is_alive'] else 0,
                'equipped_cards': len(player['equipped_cards'])
            }
            game_state['players'].append(player_info)
        
        return jsonify({
            'success': True,
            'game_state': game_state
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    print(f'客户端连接: {request.sid}')
    emit('connected', {'msg': 'Connected to server'})

@socketio.on('join_game')
def handle_join_game(data):
    """处理玩家加入游戏"""
    room_id = data['room_id']
    join_room(room_id)
    emit('joined_room', {'msg': f'加入了房间 {room_id}'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'客户端断开: {request.sid}')

if __name__ == '__main__':
    # 从环境变量获取端口，否则默认使用5000
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)