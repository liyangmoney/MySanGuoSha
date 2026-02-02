from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello, World! This is the new Flask backend for 三国杀."

@app.route('/api/config')
def game_config():
    return jsonify({
        'title': '三国杀 Online',
        'version': '1.0.0',
        'maxPlayers': 8,
        'gameModes': ['Classic', '1v1', 'Chaos']
    })

if __name__ == '__main__':
    app.run(debug=True)