import os
import atexit
from requests import get, post, exceptions
from flask import Flask, request
import time
from threading import Timer


app = Flask(__name__)

steamVR_gameid = '250820'
hellblade = '747350'
redout = '519880'
launch_cmd = 'start steam://rungameid/{0}'
close_cmd = 'taskkill /IM "{0}" /F'
game_server_manager_ip = '172.16.0.25'
# game_server_manager_ip = '192.168.0.106'
is_available = 1
player_ip = ''
launch_time = time.time()
current_game_id = ''


# Register to manager
def register_server():
    try:
        req_data = {
            'games': [hellblade, redout]
        }
        print(req_data)
        r = post('http://{0}:5000/register'.format(game_server_manager_ip), data=req_data)
    except exceptions.RequestException as e:
        raise SystemExit(e)


def unregistered():
    res = get('http://{0}:5000/deregister'.format(game_server_manager_ip))
    print(res.text)


def open_game():
    os.system(launch_cmd.format(current_game_id))
    req_data = {
        'client_ip': player_ip,
        'game_id': current_game_id,
        'connection_status': 'playing'
    }
    print('playing game ', req_data)
    r = post('http://{0}:5000/connection-status'.format(game_server_manager_ip), data=req_data)


def update_status():
    req_data = {
        'client_ip': player_ip,
        'game_id': current_game_id,
        'connection_status': 'closed'
    }
    print('closed game ', req_data)
    r = post('http://{0}:5000/connection-status'.format(game_server_manager_ip), data=req_data)


register_server()
atexit.register(unregistered)


@app.route('/')
def index():
    print('host', request.host.split(':')[0])
    print('remote_addr', request.remote_addr)
    return 'CloudXR server'


@app.route('/game-connection', methods=['POST', 'GET'])
def launch_cloudxr():
    global launch_time
    if request.method == 'POST':
        global player_ip, is_available, current_game_id
        if not is_available:
            return 'Game server not available now'
        game_title = request.form.get('game_title', type=str)
        game_id = request.form.get('game_id', type=str)
        player_ip = request.form.get('player_ip', type=str)
        print(game_title, game_id, player_ip)
        if is_available:
            is_available = 0
            current_game_id = game_id
            t = Timer(3, open_game)
            launch_time = time.time()
            t.start()
            return {'launch success': True}
        else:
            return {'launch success': False}
    # for launching steamVR process
    else:
        if time.time() > launch_time+10:
            return {'status': True}
        else:
            return {'status': False}


@app.route('/game-disconnection', methods=['POST'])
def close_clourdxr():
    global player_ip, is_available, current_game_id
    print(player_ip, request.remote_addr)
    if request.form.get('client_ip', type=str) != player_ip or request.remote_addr != game_server_manager_ip:
        return 'Invalid request'
    # Close game app and steamVR, and reset game server status
    if os.system(close_cmd.format("vrmonitor.exe")) == 0:
        update_status()
        player_ip = ''
        is_available = 1
        current_game_id = ''
        return {'status': True}
    else:
        return {'status': False}


@app.route('/stream-info')
def get_stream_info():
    return 'Under construction'


if __name__ == '__main__':
    app.run()
