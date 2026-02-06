"""
三国杀游戏服务器 - 云部署优化版
"""
import os
import sys
import json
import uuid
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.join(os.path.abspath('.'), 'sanguosha_server'))

from flask import Flask, request, jsonify, send_from_directory, session
from flask_socketio import SocketIO, emit, join_room, leave_room

# 从正确的路径导入游戏模块
from sanguosha_server.game import SanGuoShaGame
from sanguosha_server.game.player import Player
from sanguosha_server.characters import ExampleCharacter
from sanguosha_server.cards.basic_cards import Sha, Shan, Tao

app = Flask(__name__, static_folder='sanguosha_server/client')
app.config['SECRET_KEY'] = 'sanguosha_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# 游戏房间存储
rooms = {}

@app.route('/')
def index():
    return send_from_directory('sanguosha_server/client', 'index.html')

@app.route('/client.js')
def client_js():
    return send_from_directory('sanguosha_server/client', 'client.js')

@app.route('/api/create_room', methods=['POST'])
def create_room():
    """创建游戏房间"""
    try:
        room_id = str(uuid.uuid4())
        max_players = request.json.get('max_players', 2)
        
        rooms[room_id] = {
            'id': room_id,
            'game': SanGuoShaGame(),
            'players': [],
            'max_players': max_players,
            'status': 'waiting'  # waiting, running, finished
        }
        
        return jsonify({
            'success': True,
            'room_id': room_id
        })
    except Exception as e:
        print(f"Error creating room: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

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
            if player.name == player_name:
                return jsonify({'success': False, 'error': '该玩家名称已被使用'})
        
        # 创建玩家
        player = Player(player_name)
        player.character = ExampleCharacter()
        player.hp = player.character.hp
        player.max_hp = player.character.max_hp
        
        room['players'].append(player)
        room['game'].add_player(player)
        
        # 通知房间内所有玩家有新玩家加入
        socketio.emit('player_joined', {
            'player_name': player_name,
            'players': [p.name for p in room['players']],
            'room_id': room_id
        }, room=room_id)
        
        # 如果达到最大玩家数，自动开始游戏
        if len(room['players']) == room['max_players']:
            room['status'] = 'running'
            socketio.emit('game_start', {
                'players': [p.name for p in room['players']], 
                'room_id': room_id
            }, room=room_id)
        
        return jsonify({
            'success': True,
            'player_id': len(room['players']) - 1,
            'room_info': {
                'room_id': room_id,
                'players': [p.name for p in room['players']],
                'max_players': room['max_players'],
                'status': room['status']
            }
        })
    except Exception as e:
        print(f"Error joining room: {str(e)}")
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
                'players': [p.name for p in room['players']],
                'max_players': room['max_players'],
                'status': room['status']
            }
        })
    except Exception as e:
        print(f"Error getting room info: {str(e)}")
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