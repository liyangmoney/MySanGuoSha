@app.route('/api/set_ready/<room_id>', methods=['POST'])
def set_player_ready(room_id):
    """设置玩家准备状态"""
    try:
        if room_id not in rooms:
            return jsonify({'success': False, 'error': '房间不存在'})
        
        room = rooms[room_id]
        if room['status'] != 'waiting':
            return jsonify({'success': False, 'error': '游戏已经开始'})
        
        player_name = request.json.get('player_name')
        is_ready = request.json.get('is_ready', True)
        
        # 找到玩家并设置准备状态
        player = None
        for p in room['players']:
            if p['name'] == player_name:
                p['is_ready'] = is_ready
                player = p
                break
        
        if not player:
            return jsonify({'success': False, 'error': '玩家不存在'})
        
        # 广播准备状态变更
        socketio.emit('player_ready_status_changed', {
            'player_name': player_name,
            'is_ready': is_ready,
            'room_id': room_id
        }, room=room_id)
        
        # 检查是否所有玩家都准备好了
        all_ready = all(p['is_ready'] for p in room['players'])
        if all_ready and len(room['players']) == room['max_players']:
            # 所有玩家都准备好了，开始游戏
            room['status'] = 'running'
            initialize_game(room_id)
            socketio.emit('game_start', {
                'players': [{
                    'name': p['name'],
                    'character': p['character'], 
                    'hp': p['hp'],
                    'max_hp': p['max_hp'],
                    'hand_card_count': len(p['hand_cards']),
                    'is_alive': p['is_alive']
                } for p in room['players']], 
                'room_id': room_id,
                'current_player': room['players'][room['current_player_index']]['name']
            }, room=room_id)
        
        return jsonify({
            'success': True,
            'player_name': player_name,
            'is_ready': is_ready
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})