/**
 * 三国杀客户端Socket.IO通信模块
 */
class SanGuoShaClient {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.socket = null;
        this.isConnected = false;
        this.eventHandlers = {};
        this.currentRoomId = null;
        this.playerName = null;
    }

    connect() {
        this.socket = io(this.serverUrl, {
            transports: ['websocket', 'polling']
        });

        this.socket.on('connect', () => {
            console.log('已连接到三国杀服务器');
            this.isConnected = true;
            this._triggerEvent('connected');
        });

        this.socket.on('disconnect', (reason) => {
            console.log('与服务器断开连接:', reason);
            this.isConnected = false;
            this._triggerEvent('disconnected', { reason });
        });

        // 监听游戏事件
        this.socket.on('game_start', (data) => {
            this.currentRoomId = data.room_id;
            this._triggerEvent('gameStarted', data);
        });

        this.socket.on('player_joined', (data) => {
            this._triggerEvent('playerJoined', data);
        });

        this.socket.on('player_left', (data) => {
            this._triggerEvent('playerLeft', data);
        });

        this.socket.on('turn_start', (data) => {
            this._triggerEvent('turnStart', data);
        });

        this.socket.on('card_played', (data) => {
            this._triggerEvent('cardPlayed', data);
        });

        this.socket.on('game_over', (data) => {
            this._triggerEvent('gameOver', data);
        });

        this.socket.on('error', (data) => {
            this._triggerEvent('error', data);
        });
    }

    /**
     * 注册事件处理器
     */
    on(event, handler) {
        if (!this.eventHandlers[event]) {
            this.eventHandlers[event] = [];
        }
        this.eventHandlers[event].push(handler);
    }

    /**
     * 触发事件
     */
    _triggerEvent(event, data) {
        if (this.eventHandlers[event]) {
            this.eventHandlers[event].forEach(handler => handler(data));
        }
    }

    /**
     * 创建房间
     */
    createRoom(maxPlayers = 2) {
        return fetch('/api/create_room', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ max_players: maxPlayers })
        });
    }

    /**
     * 加入房间
     */
    joinRoom(roomId, playerName) {
        return fetch(`/api/join_room/${roomId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ player_name: playerName })
        });
    }

    /**
     * 获取房间信息
     */
    getRoomInfo(roomId) {
        return fetch(`/api/rooms/${roomId}`);
    }

    /**
     * 发送游戏动作
     */
    sendAction(actionData) {
        if (this.socket && this.isConnected) {
            this.socket.emit('game_action', actionData);
        }
    }

    /**
     * 加入游戏房间（WebSocket）
     */
    joinGameRoom(roomId) {
        if (this.socket && this.isConnected) {
            this.currentRoomId = roomId;
            this.socket.emit('join_game', { room_id: roomId });
        }
    }

    /**
     * 离开游戏房间
     */
    leaveGameRoom(roomId) {
        if (this.socket && this.isConnected) {
            this.socket.emit('leave_game', { room_id: roomId });
            this.currentRoomId = null;
        }
    }
}

// 全局客户端实例
const sgsClient = new SanGuoShaClient(
    window.location.hostname === 'localhost' ? 
    'http://localhost:5000' : 
    window.location.protocol + '//' + window.location.hostname + (window.location.port ? ':' + window.location.port : '')
);

// 初始化
sgsClient.connect();

// 导出给全局使用
window.SanGuoShaClient = sgsClient;