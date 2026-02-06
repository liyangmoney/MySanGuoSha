/**
 * 三国杀客户端Socket.IO通信模块
 */
class SanGuoShaClient {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.eventHandlers = {};
        this.currentRoomId = null;
        this.playerName = null;
        
        // 根据当前环境确定服务器URL
        this.serverUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ?
            'http://localhost:5000' :
            window.location.protocol + '//' + window.location.hostname + (window.location.port ? ':' + window.location.port : '');
    }

    connect() {
        this.socket = io(this.serverUrl, {
            transports: ['websocket', 'polling'],
            withCredentials: false
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

        this.socket.on('joined_room', (data) => {
            this._triggerEvent('joinedRoom', data);
        });

        this.socket.on('connected', (data) => {
            this._triggerEvent('serverConnected', data);
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
    async createRoom(maxPlayers = 2) {
        try {
            const response = await fetch('/api/create_room', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ max_players: maxPlayers })
            });
            return response;
        } catch (error) {
            console.error('创建房间时发生错误:', error);
            throw error;
        }
    }

    /**
     * 加入房间
     */
    async joinRoom(roomId, playerName) {
        try {
            const response = await fetch(`/api/join_room/${roomId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ player_name: playerName })
            });
            return response;
        } catch (error) {
            console.error('加入房间时发生错误:', error);
            throw error;
        }
    }

    /**
     * 获取房间信息
     */
    async getRoomInfo(roomId) {
        try {
            const response = await fetch(`/api/rooms/${roomId}`);
            return response;
        } catch (error) {
            console.error('获取房间信息时发生错误:', error);
            throw error;
        }
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
const sgsClient = new SanGuoShaClient();

// 初始化
sgsClient.connect();

// 确保全局可用
window.SanGuoShaClient = sgsClient;
window.sgsClient = sgsClient;

// 保持向后兼容性
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SanGuoShaClient;
}